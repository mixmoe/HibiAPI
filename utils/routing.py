import inspect
from enum import Enum
from fnmatch import fnmatch
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple
from urllib.parse import ParseResult, urlparse

from fastapi.routing import APIRouter
from httpx import URL
from pydantic import AnyHttpUrl, validate_arguments
from pydantic.errors import UrlHostError

from .net import AsyncHTTPClient


def exclude_params(func: Callable, params: Mapping[str, Any]) -> Dict[str, Any]:
    func_params = inspect.signature(func).parameters
    return {k: v for k, v in params.items() if k in func_params}


class SlashRouter(APIRouter):
    def api_route(self, path: str, **kwargs):
        path = path if path.startswith("/") else ("/" + path)
        return super().api_route(path, **kwargs)


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


class BaseHostUrl(AnyHttpUrl):
    allowed_hosts: List[str] = []

    @classmethod
    def validate_host(
        cls, parts: Dict[str, str]
    ) -> Tuple[str, Optional[str], str, bool]:
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
