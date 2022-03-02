import functools
from types import TracebackType
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    Optional,
    Type,
    TypeVar,
    Union,
)

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

AsyncCallable_T = TypeVar("AsyncCallable_T", bound=Callable[..., Coroutine])


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
    client: AsyncHTTPClient

    def __init__(
        self,
        headers: Optional[Dict[str, Any]] = None,
        cookies: Optional[Cookies] = None,
        proxies: Optional[Dict[str, str]] = None,
        client_class: Type[AsyncHTTPClient] = AsyncHTTPClient,
    ):
        self.cookies, self.client_class = cookies or Cookies(), client_class
        self.headers: Dict[str, Any] = headers or {}
        self.proxies: Any = proxies or {}  # Bypass type checker

        self.create_client()

    def create_client(self):
        self.client = self.client_class(
            headers=self.headers,
            proxies=self.proxies,
            cookies=self.cookies,
            http2=True,
            follow_redirects=True,
        )
        return self.client

    async def __aenter__(self) -> AsyncHTTPClient:
        if self.client.is_closed:
            self.client = await self.create_client().__aenter__()
        return self.client

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ):
        if not (exc_type and exc_value and traceback):
            return
        if not self.client.is_closed:
            await self.client.__aexit__(exc_type, exc_value, traceback)
        return


def catch_network_error(function: AsyncCallable_T) -> AsyncCallable_T:
    timed_func = TimeIt(function)

    @functools.wraps(timed_func)
    async def wrapper(*args, **kwargs):
        try:
            return await timed_func(*args, **kwargs)
        except HTTPStatusError as e:
            raise UpstreamAPIException(detail=e.response.text) from e
        except HTTPError as e:
            raise UpstreamAPIException from e

    return wrapper  # type:ignore
