import hashlib
from datetime import timedelta
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple, TypeVar, cast

from cashews import Cache
from pydantic import BaseModel
from pydantic.decorator import ValidatedFunction

from .config import Config
from .log import logger

CACHE_CONFIG_KEY = "_cache_config"

AsyncFunc = Callable[..., Awaitable[Any]]
T_AsyncFunc = TypeVar("T_AsyncFunc", bound=AsyncFunc)


CACHE_ENABLED = Config["cache"]["enabled"].as_bool()
CACHE_DELTA = timedelta(seconds=Config["cache"]["ttl"].as_number())
CACHE_URI = Config["cache"]["uri"].as_str()
CACHE_CONTROLLABLE = Config["cache"]["controllable"].as_bool()

cache = Cache(name="hibiapi")
try:
    cache.setup(CACHE_URI)
except Exception as e:
    logger.warning(
        f"Cache URI <y>{CACHE_URI!r}</y> setup <r><b>failed</b></r>: "
        f"<r>{e!r}</r>, use memory backend instead."
    )


class CacheConfig(BaseModel):
    endpoint: AsyncFunc
    namespace: str
    enabled: bool = True
    ttl: timedelta = CACHE_DELTA

    @staticmethod
    def new(
        function: AsyncFunc,
        *,
        enabled: bool = True,
        ttl: timedelta = CACHE_DELTA,
        namespace: Optional[str] = None,
    ):
        return CacheConfig(
            endpoint=function,
            enabled=enabled,
            ttl=ttl,
            namespace=namespace or function.__qualname__,
        )


def cache_config(
    enabled: bool = True,
    ttl: timedelta = CACHE_DELTA,
    namespace: Optional[str] = None,
):
    def decorator(function: T_AsyncFunc) -> T_AsyncFunc:
        setattr(
            function,
            CACHE_CONFIG_KEY,
            CacheConfig.new(function, enabled=enabled, ttl=ttl, namespace=namespace),
        )
        return function

    return decorator


disable_cache = cache_config(enabled=False)


class CachedValidatedFunction(ValidatedFunction):
    def serialize(self, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> BaseModel:
        values = self.build_values(args=args, kwargs=kwargs)
        return self.model(**values)


def endpoint_cache(function: T_AsyncFunc) -> T_AsyncFunc:
    from .routing import request_headers, response_headers

    vf = CachedValidatedFunction(function, config={})
    config = cast(
        CacheConfig,
        getattr(function, CACHE_CONFIG_KEY, None) or CacheConfig.new(function),
    )

    config.enabled = CACHE_ENABLED and config.enabled

    @wraps(function)
    async def wrapper(*args, **kwargs):
        cache_policy = "public"

        if CACHE_CONTROLLABLE:
            cache_policy = request_headers.get().get("cache-control", cache_policy)

        if not config.enabled or cache_policy.casefold() == "no-store":
            return await vf.call(*args, **kwargs)

        key = (
            f"{config.namespace}:"
            + hashlib.md5(
                (model := vf.serialize(args=args, kwargs=kwargs))
                .json(exclude={"self"}, sort_keys=True, ensure_ascii=False)
                .encode()
            ).hexdigest()
        )

        response_header = response_headers.get()
        result: Optional[Any] = None

        if cache_policy.casefold() == "no-cache":
            await cache.delete(key)
        elif result := await cache.get(key):
            logger.debug(f"Request hit cache <b><e>{key}</e></b>")
            response_header.setdefault("X-Cache-Hit", key)

        if result is None:
            result = await vf.execute(model)
            await cache.set(key, result, expire=config.ttl)

        if (cache_remain := await cache.get_expire(key)) > 0:
            response_header.setdefault("Cache-Control", f"max-age={cache_remain}")

        return result

    return wrapper  # type:ignore
