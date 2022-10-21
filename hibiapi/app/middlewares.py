from datetime import datetime
from typing import Awaitable, Callable, List

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.httpx import HttpxIntegration
from starlette.datastructures import MutableHeaders

from hibiapi.utils.config import Config
from hibiapi.utils.exceptions import BaseServerException, UncaughtException
from hibiapi.utils.log import LoguruHandler, logger
from hibiapi.utils.routing import request_headers, response_headers

from .application import app
from .handlers import exception_handler

RequestHandler = Callable[[Request], Awaitable[Response]]


if Config["server"]["gzip"].as_bool():
    app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config["server"]["cors"]["origins"].get(List[str]),
    allow_credentials=Config["server"]["cors"]["credentials"].as_bool(),
    allow_methods=Config["server"]["cors"]["methods"].get(List[str]),
    allow_headers=Config["server"]["cors"]["headers"].get(List[str]),
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=Config["server"]["allowed"].get(List[str]),
)
app.add_middleware(SentryAsgiMiddleware)

HttpxIntegration.setup_once()


@app.middleware("http")
async def request_logger(request: Request, call_next: RequestHandler) -> Response:
    start_time = datetime.now()
    host, port = request.client or (None, None)
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds() * 1000
    response_headers.get().setdefault("X-Process-Time", f"{process_time:.3f}")
    bg, fg = (
        ("green", "red")
        if response.status_code < 400
        else ("yellow", "blue")
        if response.status_code < 500
        else ("red", "green")
    )
    status_code, method = response.status_code, request.method.upper()
    user_agent = (
        LoguruHandler.escape_tag(request.headers["user-agent"])
        if "user-agent" in request.headers
        else "<d>Unknown</d>"
    )
    logger.info(
        f"<m><b>{host}</b>:{port}</m>"
        f" | <{bg.upper()}><b><{fg}>{method}</{fg}></b></{bg.upper()}>"
        f" | <n><b>{str(request.url)!r}</b></n>"
        f" | <c>{process_time:.3f}ms</c>"
        f" | <e>{user_agent}</e>"
        f" | <b><{bg}>{status_code}</{bg}></b>"
    )
    return response


@app.middleware("http")
async def contextvar_setter(request: Request, call_next: RequestHandler):
    request_headers.set(request.headers)
    response_headers.set(MutableHeaders())
    response = await call_next(request)
    response.headers.update({**response_headers.get()})
    return response


@app.middleware("http")
async def uncaught_exception_handler(
    request: Request, call_next: RequestHandler
) -> Response:
    try:
        response = await call_next(request)
    except Exception as error:
        response = await exception_handler(
            request,
            exc=(
                error
                if isinstance(error, BaseServerException)
                else UncaughtException.with_exception(error)
            ),
        )
    return response
