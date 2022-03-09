import base64
import hashlib
import pickle
import pickletools
import time
import zlib
from datetime import timedelta
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple, TypeVar, cast

from aiocache import Cache as AioCache  # type:ignore
from aiocache.base import BaseCache  # type:ignore
from aiocache.serializers import BaseSerializer  # type:ignore
from pydantic import BaseModel
from pydantic.decorator import ValidatedFunction

from .config import Config
from .log import logger

CACHE_CONFIG_KEY = "_cache_config"

CACHE_ENABLED = Config["cache"]["enabled"].as_bool()
CACHE_DELTA = timedelta(seconds=Config["cache"]["ttl"].as_number())
CACHE_URI = Config["cache"]["uri"].as_str()

AsyncFunc = Callable[..., Awaitable[Any]]
T_AsyncFunc = TypeVar("T_AsyncFunc", bound=AsyncFunc)


class GZippedBase85Serializer(BaseSerializer):
    def dumps(self, value: Any) -> str:
        return base64.b85encode(
            zlib.compress(
                pickletools.optimize(
                    pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                ),
                level=zlib.Z_BEST_COMPRESSION,
            ),
        ).decode()

    def loads(self, value: Optional[str]) -> Any:
        return (
            pickle.loads(
                zlib.decompress(base64.b85decode(value)),
            )
            if value
            else None
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
        return self.model(**values)  # type:ignore


def endpoint_cache(function: T_AsyncFunc) -> T_AsyncFunc:
    from .routing import request_headers, response_headers

    vf = CachedValidatedFunction(function, config={})
    cache = cast(BaseCache, AioCache.from_url(CACHE_URI))
    config = cast(
        CacheConfig,
        getattr(function, CACHE_CONFIG_KEY, None) or CacheConfig.new(function),
    )

    cache.namespace, cache.ttl = config.namespace, config.ttl.total_seconds()
    cache.serializer = GZippedBase85Serializer(encoding="utf-8")

    if not CACHE_ENABLED:
        config.enabled = False

    @wraps(function)
    async def wrapper(*args, **kwargs):
        cache_policy: str = request_headers.get().get("cache-control", "public")

        if (
            not config.enabled
            or cache.ttl is None
            or cache_policy.casefold() == "no-store"
        ):
            return await vf.call(*args, **kwargs)

        key = hashlib.md5(
            (model := vf.serialize(args=args, kwargs=kwargs))
            .json(exclude={"self"}, sort_keys=True, ensure_ascii=False)
            .encode()
        ).hexdigest()

        response_header = response_headers.get()
        cache_result: Optional[Tuple[Any, float]] = None

        if cache_policy.casefold() == "no-cache":
            await cache.delete(key)
        elif cache_result := await cache.get(key):
            logger.debug(f"Request hit cache <e>{cache.namespace}</e>:<g>{key}</g>")
            response_header.setdefault("X-Cache-Hit", key)

        now_time = time.time()

        if cache_result is None:
            cache_result = await vf.execute(model), now_time
            await cache.set(key, cache_result)

        return_result, cache_time = cache_result

        if (cache_remain := int(cache_time + cache.ttl - now_time)) > 0:
            response_header.setdefault("Cache-Control", f"max-age={cache_remain}")

        return return_result

    return wrapper  # type:ignore
