from datetime import datetime
from typing import Any, Callable, Coroutine

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ValidationError
from utils.config import Config
from utils.exceptions import (
    RESPONSE_CONDITIONS,
    BaseServerException,
    ClientSideException,
    ExceptionStorage,
    ServerSideException,
)
from utils.log import logger

from app.bilibili import router as BilibiliRouter
from app.pixiv import router as PixivRouter

app = FastAPI(
    debug=Config["debug"].as_bool(),
    title="HibiAPI",
    version=Config["version"].as_str(),
    description="An alternative implement of Imjad API",
    docs_url="/docs/test",
    redoc_url="/docs",
    responses=RESPONSE_CONDITIONS,  # type:ignore
)
app.include_router(PixivRouter, prefix="/pixiv")
app.include_router(BilibiliRouter, prefix="/bilibili")
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config["server"]["cors"]["origins"].as_iterable(list),
    allow_credentials=Config["server"]["cors"]["credentials"].as_bool(),
    allow_methods=Config["server"]["cors"]["methods"].as_iterable(list),
    allow_headers=Config["server"]["cors"]["headers"].as_iterable(list),
)


@app.get("/", include_in_schema=False)
async def redirect():
    return Response(status_code=302, headers={"Location": "/docs"})


@app.exception_handler(HTTPException)
async def exceptionHandler(request: Request, exc: HTTPException):
    content = {"url": str(request.url), "detail": exc.detail, "code": exc.status_code}
    if isinstance(exc, BaseServerException):
        content.update(exc.extra)
    if exc.status_code >= 500:
        trace = ExceptionStorage.save(exc.__traceback__.__str__())
        logger.opt(exception=exc, colors=True).error(
            f"Exception occurred on <y>{request.url}</y> <R><b>({trace})</b></R>:"
        )
        content.update({"trace": ExceptionStorage.save(exc.__traceback__.__str__())})
    return JSONResponse(content, exc.status_code)


@app.exception_handler(AssertionError)
async def assertionHandler(request: Request, exc: AssertionError):
    return await exceptionHandler(request, ClientSideException(detail=str(exc)))


@app.exception_handler(ValidationError)
async def validationHandler(request: Request, exc: ValidationError):
    return await exceptionHandler(
        request, ClientSideException(detail=str(exc), code=422, validation=exc.errors())
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
            request, ServerSideException().with_traceback(e.__traceback__)
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
                f"<c>{round(processTime,5)}ms</c>",
                f"<e>{request.headers.get('user-agent','<d>Unknown</d>')}</e>",
                f"<b><{logColor}>{response.status_code}</{logColor}></b>",
            ]
        )
    )
    return response
