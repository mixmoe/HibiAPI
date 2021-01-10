import asyncio
from datetime import datetime
from typing import Any, Callable, Coroutine, List, NoReturn

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError as FastAPIValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic.error_wrappers import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

#
from utils.config import Config
from utils.exceptions import (
    BaseHTTPException,
    BaseServerException,
    ClientSideException,
    ExceptionReturn,
    ExceptionStorage,
    UncaughtException,
    ValidationException,
)
from utils.log import logger
from utils.temp import TempFile

from app.bilibili import router as BilibiliRouter
from app.netease import router as NeteaseRouter
from app.pixiv import router as PixivRouter
from app.qrcode import router as QRCodeRouter

app = FastAPI(
    debug=Config["debug"].as_bool(),
    title="HibiAPI",
    version=Config["version"].as_str(),
    description="An alternative implement of Imjad API",
    docs_url="/docs/test",
    redoc_url="/docs",
    responses={
        code: {
            "model": ExceptionReturn,
        }
        for code in (400, 422, 500, 502)
    },
)

app.include_router(PixivRouter, prefix="/pixiv")
app.include_router(BilibiliRouter, prefix="/bilibili")
app.include_router(QRCodeRouter, prefix="/qrcode")
app.include_router(NeteaseRouter, prefix="/netease")

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config["server"]["cors"]["origins"].get(List[str]),
    allow_credentials=Config["server"]["cors"]["credentials"].as_bool(),
    allow_methods=Config["server"]["cors"]["methods"].get(List[str]),
    allow_headers=Config["server"]["cors"]["headers"].get(List[str]),
)
app.mount(
    "/temp",
    StaticFiles(directory=str(TempFile.path), check_dir=False),
    "Temporary file directory",
)


@app.on_event("startup")
async def cleaner():
    async def clean() -> NoReturn:
        while True:
            try:
                await TempFile.clean()
            except Exception:
                logger.exception("Exception occurred during executing cleaning task:")
            await asyncio.sleep(3600)

    asyncio.ensure_future(clean())


@app.get("/", include_in_schema=False)
async def redirect():
    return Response(status_code=302, headers={"Location": "/docs"})


@app.exception_handler(BaseServerException)
async def exceptionHandler(request: Request, exc: BaseServerException) -> JSONResponse:
    exc.data.url = str(request.url)  # type:ignore
    try:
        raise exc
    except UncaughtException as e:
        exc.data.trace = ExceptionStorage.save(e.exc.__traceback__)
    except BaseServerException:
        pass
    if exc.data.code >= 500:
        logger.opt(exception=exc).exception(
            f"Error occurred during parsing <r><b>({exc.data=})</b></r>:"
        )
    return JSONResponse(
        content=exc.data.dict(exclude_none=True, exclude_defaults=True),
        headers=exc.data.headers,
        status_code=exc.data.code,
    )


@app.exception_handler(StarletteHTTPException)
async def overrideHandler(request: Request, exc: StarletteHTTPException):
    return await exceptionHandler(
        request,
        BaseHTTPException(
            exc.detail,
            code=exc.status_code,
            headers={} if not isinstance(exc, FastAPIHTTPException) else exc.headers,
        ),
    )


@app.exception_handler(AssertionError)
async def assertionHandler(request: Request, exc: AssertionError):
    return await exceptionHandler(
        request, ClientSideException(detail=f"Assertion: {exc}")
    )


@app.exception_handler(FastAPIValidationError)
@app.exception_handler(PydanticValidationError)
async def validationHandler(request: Request, exc: PydanticValidationError):
    return await exceptionHandler(
        request, ValidationException(detail=str(exc), validation=exc.errors())
    )


@app.middleware("http")
async def responseMiddleware(
    request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]
) -> Response:
    startTime = datetime.now()
    try:
        response = await call_next(request)
    except Exception as e:
        response = await exceptionHandler(
            request,
            UncaughtException.with_exception(e),
        )
    processTime = (datetime.now() - startTime).total_seconds() * 1000
    response.headers["X-Process-Time"] = f"{processTime:.3f}"
    logColor = (
        "green"
        if response.status_code < 400
        else "yellow"
        if response.status_code < 500
        else "red"
    )
    logger.info(
        "|".join(
            [
                f"<{logColor.upper()}><b>{request.method.upper()}</b></{logColor.upper()}>",  # noqa:E501
                f"<n><b>{str(request.url)!r}</b></n>",
                f"<c>{processTime:.3f}ms</c>",
                f"<e>{request.headers.get('user-agent','<d>Unknown</d>')}</e>",
                f"<b><{logColor}>{response.status_code}</{logColor}></b>",
            ]
        )
    )
    return response
