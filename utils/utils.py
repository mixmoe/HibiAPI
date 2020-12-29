from enum import Enum
from threading import current_thread
from types import TracebackType
from typing import Any, Dict, Optional, Type
from urllib.parse import ParseResult, urlparse

from fastapi.routing import APIRouter
from httpx import URL, AsyncClient, Cookies, HTTPError
from pydantic import Extra, validate_arguments

from .decorators import Retry
from .exceptions import UpstreamAPIException


class SlashRouter(APIRouter):
    def api_route(self, path: str, **kwargs):
        return super().api_route(
            path=(path if path.startswith("/") else ("/" + path)), **kwargs
        )


class AsyncHTTPClient(AsyncClient):
    @Retry
    async def request(self, *args, **kwargs):
        try:
            return await super().request(*args, **kwargs)
        except HTTPError:
            raise UpstreamAPIException


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

    async def __aenter__(self) -> AsyncHTTPClient:
        tid = current_thread().ident or 1
        if tid not in self.clients:
            self.clients[tid] = AsyncHTTPClient(
                headers=self.headers,
                proxies=self.proxies,  # type:ignore
                cookies=self.cookies,
            )
        return await self.clients[tid].__aenter__()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ):
        if exc_type is None:
            return
        tid = current_thread().ident or 1
        if tid not in self.clients:
            return
        await self.clients.pop(tid).__aexit__(exc_type, exc_value, traceback)


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
        return validate_arguments(
            obj,
            config={
                "extra": Extra.forbid,
                "use_enum_values": True,
                "allow_mutation": False,
            },
        )
