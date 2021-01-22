import asyncio
import inspect
from enum import Enum
from threading import current_thread
from types import TracebackType
from typing import Any, Callable, Dict, Mapping, Optional, Type, Union
from urllib.parse import ParseResult, urlparse

from fastapi.routing import APIRouter
from httpx import URL, AsyncClient, Cookies, Request, Response, TransportError
from pydantic import validate_arguments

from .decorators import Retry
from .log import logger


def exclude_params(func: Callable, params: Mapping[str, Any]) -> Dict[str, Any]:
    func_params = inspect.signature(func).parameters
    return {k: v for k, v in params.items() if k in func_params}


class SlashRouter(APIRouter):
    def api_route(self, path: str, **kwargs):
        path = path if path.startswith("/") else ("/" + path)
        return super().api_route(path, **kwargs)


class AsyncHTTPClient(AsyncClient):
    @Retry(exceptions=[TransportError])
    async def request(self, method: str, url: Union[URL, str], **kwargs):
        return await super().request(method, url, **kwargs)


class BaseNetClient:
    def __init__(
        self,
        headers: Optional[Dict[str, Any]] = None,
        cookies: Optional[Cookies] = None,
        proxies: Optional[Dict[str, str]] = None,
    ):
        self.headers: Dict[str, Any] = headers or {}
        self.cookies: Cookies = cookies or Cookies()
        self.proxies: Dict[str, str] = proxies or {}
        self.clients: Dict[int, AsyncHTTPClient] = {}

    @staticmethod
    async def _log_request(request: Request):
        method, url = request.method, request.url
        logger.debug(
            f"Network request <y>sent</y>: <b><e>{method}</e> <u>{url}</u></b>"
        )

    @staticmethod
    async def _log_response(response: Response):
        method, url = response.request.method, response.url
        length, code = len(response.content), response.status_code
        logger.debug(
            f"Network request <g>finished</g>: <b><e>{method}</e> "
            f"<u>{url}</u> <m>{code}</m></b> <m>{length}</m>"
        )

    async def __aenter__(self) -> AsyncHTTPClient:
        tid = current_thread().ident or 1
        if tid not in self.clients:
            self.clients[tid] = AsyncHTTPClient(
                headers=self.headers,
                proxies=self.proxies,  # type:ignore
                cookies=self.cookies,
                event_hooks={
                    "request": [self._log_request],
                    "response": [self._log_response],
                },
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


class BaseEndpoint:
    type_checking: bool = True

    def __init__(self, client: AsyncHTTPClient):
        self.client = client

    @staticmethod
    def _join(base: str, endpoint: str, params: Dict[str, Any]) -> URL:
        host: ParseResult = urlparse(base)
        params = {
            k: (v.value if isinstance(v, Enum) else v)
            for k, v in params.items()
            if v is not None
        }
        return URL(
            url=ParseResult(
                scheme=host.scheme,
                netloc=host.netloc,
                path=endpoint.format(**params),
                params="",
                query="",
                fragment="",
            ).geturl(),
            params=params,
        )

    def __getattribute__(self, name: str) -> Any:
        obj = super().__getattribute__(name)
        if name.startswith("_"):
            return obj
        elif not callable(obj):
            return obj
        elif not self.type_checking:
            return obj
        return validate_arguments(obj)
