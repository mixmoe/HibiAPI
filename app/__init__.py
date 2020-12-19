from datetime import datetime
from typing import Any, Callable, Coroutine, Optional

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ValidationError
from utils.config import Config
from utils.exceptions import RESPONSE_CONDITIONS, ExceptionStorage, ServerSideException
from utils.log import logger

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


@app.exception_handler(HTTPException)
async def exceptionHandler(request: Request, exc: HTTPException):
    trace: Optional[str] = None
    try:
        if exc.status_code >= 500:
            raise exc
    except HTTPException as e:
        trace = ExceptionStorage.save(e.__traceback__.__str__())
        logger.exception(f"Server side exception occurred during processing ({trace}):")
    return JSONResponse(
        content={"detail": exc.detail, "code": exc.status_code, "trace": trace},
        status_code=exc.status_code,
    )


@app.exception_handler(ValidationError)
async def validationHandler(request: Request, exc: ValidationError):
    return JSONResponse(content={"detail": exc.errors()}, status_code=422)


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
                f"<{logColor.upper()}><w>{request.method.upper()}</w></{logColor.upper()}>",  # noqa:E501
                f"<n><b>{str(request.url)!r}</b></n>",
                f"<c>{round(processTime,5)}ms</c>",
                f"<e>{request.headers.get('user-agent','<d>Unknown</d>')}</e>",
                f"<b><{logColor}>{response.status_code}</{logColor}></b>",
            ]
        )
    )
    return response
