from datetime import datetime
from typing import Any, Callable, Coroutine, List

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from utils.config import Config
from utils.exceptions import UncaughtException
from utils.log import logger

from .application import app
from .handlers import exceptionHandler

if Config["server"]["gzip"].as_bool():
    app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config["server"]["cors"]["origins"].get(List[str]),
    allow_credentials=Config["server"]["cors"]["credentials"].as_bool(),
    allow_methods=Config["server"]["cors"]["methods"].get(List[str]),
    allow_headers=Config["server"]["cors"]["headers"].get(List[str]),
)
app.add_middleware(SentryAsgiMiddleware)


@app.middleware("http")
async def uncaught_exception_handler(
    request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]
) -> Response:
    try:
        response = await call_next(request)
    except Exception as error:
        response = await exceptionHandler(
            request, exc=UncaughtException.with_exception(error)
        )
    return response


@app.middleware("http")
async def request_log_handler(
    request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]
) -> Response:
    start_time = datetime.now()
    host, port = request.client
    try:
        response = await call_next(request)
    except Exception as e:
        response = await exceptionHandler(
            request,
            UncaughtException.with_exception(e),
        )
    process_time = (datetime.now() - start_time).total_seconds() * 1000
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    color = (
        "green"
        if response.status_code < 400
        else "yellow"
        if response.status_code < 500
        else "red"
    )
    logger.info(
        " | ".join(
            [
                f"<m><b>{host}</b>:{port}</m>",
                f"<{color.upper()}><b>{request.method.upper()}</b></{color.upper()}>",
                f"<n><b>{str(request.url)!r}</b></n>",
                f"<c>{process_time:.3f}ms</c>",
                f"<e>{request.headers.get('user-agent','<d>Unknown</d>')}</e>",
                f"<b><{color}>{response.status_code}</{color}></b>",
            ]
        )
    )
    return response
