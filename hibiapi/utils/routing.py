import inspect
from contextvars import ContextVar
from enum import Enum
from fnmatch import fnmatch
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Mapping, Optional, Tuple, Type
from urllib.parse import ParseResult, urlparse

from fastapi import Depends, Request
from fastapi.routing import APIRouter
from httpx import URL
from pydantic import AnyHttpUrl
from pydantic.errors import UrlHostError
from starlette.datastructures import Headers, MutableHeaders

from hibiapi.utils.cache import endpoint_cache
from hibiapi.utils.net import AsyncCallable_T, AsyncHTTPClient, BaseNetClient

DONT_ROUTE_KEY = "_dont_route"


def dont_route(func: AsyncCallable_T) -> AsyncCallable_T:
    setattr(func, DONT_ROUTE_KEY, True)
    return func


class EndpointMeta(type):
    @staticmethod
    def _list_router_function(members: Dict[str, Any]):
        return {
            name: object
            for name, object in members.items()
            if (
                inspect.iscoroutinefunction(object)
                and not name.startswith("_")
                and not getattr(object, DONT_ROUTE_KEY, False)
            )
        }

    def __new__(
        cls,
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
        *,
        cache_endpoints: bool = True,
        **kwargs,
    ):
        for object_name, object in cls._list_router_function(namespace).items():
            namespace[object_name] = (
                endpoint_cache(object) if cache_endpoints else object
            )
        return super().__new__(cls, name, bases, namespace, **kwargs)

    @property
    def router_functions(self):
        return self._list_router_function(dict(inspect.getmembers(self)))


class BaseEndpoint(metaclass=EndpointMeta, cache_endpoints=False):
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


class SlashRouter(APIRouter):
    def api_route(self, path: str, **kwargs):
        path = path if path.startswith("/") else f"/{path}"
        return super().api_route(path, **kwargs)


class EndpointRouter(SlashRouter):
    @staticmethod
    def _exclude_params(func: Callable, params: Mapping[str, Any]) -> Dict[str, Any]:
        func_params = inspect.signature(func).parameters
        return {k: v for k, v in params.items() if k in func_params}

    @staticmethod
    def _router_signature_convert(
        func,
        endpoint_class: Type["BaseEndpoint"],
        request_client: Callable,
        method_name: Optional[str] = None,
    ):
        @wraps(func)
        async def route_func(endpoint: endpoint_class, **kwargs):
            endpoint_method = getattr(endpoint, method_name or func.__name__)
            return await endpoint_method(**kwargs)

        route_func.__signature__ = inspect.signature(route_func).replace(
            parameters=[
                inspect.Parameter(
                    name="endpoint",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=endpoint_class,
                    default=Depends(request_client),
                ),
                *(
                    param
                    for param in inspect.signature(func).parameters.values()
                    if param.kind == inspect.Parameter.KEYWORD_ONLY
                ),
            ]
        )
        return route_func

    def include_endpoint(
        self,
        endpoint_class: Type[BaseEndpoint],
        net_client: BaseNetClient,
        add_match_all: bool = True,
    ):
        router_functions = endpoint_class.router_functions

        async def request_client():
            async with net_client as client:
                yield endpoint_class(client)

        for func_name, func in router_functions.items():
            self.add_api_route(
                path=f"/{func_name}",
                endpoint=self._router_signature_convert(
                    func,
                    endpoint_class=endpoint_class,
                    request_client=request_client,
                    method_name=func_name,
                ),
                methods=["GET"],
            )

        if not add_match_all:
            return

        @self.get("/", description="JournalAD style API routing", deprecated=True)
        async def match_all(
            request: Request,
            type: Literal[tuple(router_functions.keys())],  # type: ignore
            endpoint: endpoint_class = Depends(request_client),
        ):
            func = router_functions[type]
            return await func(
                endpoint, **self._exclude_params(func, request.query_params)
            )


class BaseHostUrl(AnyHttpUrl):
    allowed_hosts: List[str] = []

    @classmethod
    def validate_host(cls, parts) -> Tuple[str, Optional[str], str, bool]:
        host, tld, host_type, rebuild = super().validate_host(parts)
        if not cls._check_domain(host):
            raise UrlHostError(allowed=cls.allowed_hosts)
        return host, tld, host_type, rebuild

    @classmethod
    def _check_domain(cls, host: str) -> bool:
        return any(
            filter(
                lambda x: fnmatch(host, x),  # type:ignore
                cls.allowed_hosts,
            )
        )


request_headers = ContextVar[Headers]("request_headers")
response_headers = ContextVar[MutableHeaders]("response_headers")
