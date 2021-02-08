import asyncio
from functools import wraps
from threading import current_thread
from types import TracebackType
from typing import Any, Callable, Coroutine, Dict, Optional, Type, TypeVar, Union

from httpx import (
    URL,
    AsyncClient,
    Cookies,
    HTTPError,
    HTTPStatusError,
    Request,
    Response,
    ResponseNotRead,
    TransportError,
)

from .decorators import Retry, TimeIt
from .exceptions import UpstreamAPIException
from .log import logger

_AsyncCallable = TypeVar("_AsyncCallable", bound=Callable[..., Coroutine])


class AsyncHTTPClient(AsyncClient):
    @staticmethod
    async def _log_request(request: Request):
        method, url = request.method, request.url
        logger.debug(
            f"Network request <y>sent</y>: <b><e>{method}</e> <u>{url}</u></b>"
        )

    @staticmethod
    async def _log_response(response: Response):
        method, url = response.request.method, response.url
        try:
            length, code = len(response.content), response.status_code
        except ResponseNotRead:
            length, code = -1, response.status_code
        logger.debug(
            f"Network request <g>finished</g>: <b><e>{method}</e> "
            f"<u>{url}</u> <m>{code}</m></b> <m>{length}</m>"
        )

    @Retry(exceptions=[TransportError])
    async def request(self, method: str, url: Union[URL, str], **kwargs):
        self.event_hooks = {
            "request": [self._log_request],
            "response": [self._log_response],
        }
        return await super().request(method, url, **kwargs)


class BaseNetClient:
    def __init__(
        self,
        headers: Optional[Dict[str, Any]] = None,
        cookies: Optional[Cookies] = None,
        proxies: Optional[Dict[str, str]] = None,
        client_class: Optional[Type[AsyncHTTPClient]] = None,
    ):
        self.headers: Dict[str, Any] = headers or {}
        self.cookies: Cookies = cookies or Cookies()
        self.proxies: Dict[str, str] = proxies or {}
        self.clients: Dict[int, AsyncHTTPClient] = {}
        self.client_class: Type[AsyncHTTPClient] = client_class or AsyncHTTPClient

    async def __aenter__(self) -> AsyncHTTPClient:
        tid = current_thread().ident or 1
        if tid not in self.clients:
            self.clients[tid] = self.client_class(
                headers=self.headers,
                proxies=self.proxies,  # type:ignore
                cookies=self.cookies,
                http2=True,
            )
        return await self.clients[tid].__aenter__()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ):
        if exc_type is None:
            return
        tid = current_thread().ident or 1
        if tid not in self.clients:
            return
        await self.clients.pop(tid).__aexit__(exc_type, exc_value, traceback)

    def __del__(self):
        try:
            asyncio.get_event_loop()
        except ImportError:
            return
        asyncio.ensure_future(
            asyncio.gather(
                *map(
                    lambda f: f.aclose(),
                    self.clients.values(),
                ),
            )
        )


def catch_network_error(function: _AsyncCallable) -> _AsyncCallable:
    function = TimeIt(function)

    @wraps(function)
    async def wrapper(*args, **kwargs):
        try:
            return await function(*args, **kwargs)
        except HTTPStatusError as e:
            raise UpstreamAPIException(detail=e.response.text) from e
        except HTTPError as e:
            raise UpstreamAPIException from e

    return wrapper  # type:ignore
