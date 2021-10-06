from datetime import datetime
from typing import Any, Callable, Coroutine, List, Optional, Set

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.httpx import HttpxIntegration
from starlette.datastructures import MutableHeaders

from hibiapi.utils.config import Config
from hibiapi.utils.exceptions import (
    BaseServerException,
    ClientSideException,
    UncaughtException,
)
from hibiapi.utils.log import logger
from hibiapi.utils.routing import request_headers, response_headers

from .application import app
from .handlers import exception_handler

HttpxIntegration.setup_once()

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

RequestHandler = Callable[[Request], Coroutine[Any, Any, Response]]

ALLOWED_DOMAINS = Config["server"]["domains"].get(Optional[Set[str]])  # type: ignore


@app.middleware("http")
async def domain_limiter(request: Request, call_next: RequestHandler) -> Response:
    if (ALLOWED_DOMAINS is not None) and (
        (domain := request.url.netloc) not in ALLOWED_DOMAINS
    ):
        raise ClientSideException(f"{domain=} is not allowed.", code=403)
    return await call_next(request)


@app.middleware("http")
async def request_logger(request: Request, call_next: RequestHandler) -> Response:
    start_time = datetime.now()
    host, port = request.client
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds() * 1000
    response_headers.get().setdefault("X-Process-Time", f"{process_time:.3f}")
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
