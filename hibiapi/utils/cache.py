import base64
import hashlib
import pickle
import pickletools
import time
import zlib
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple, TypeVar

from aiocache import Cache as AioCache  # type:ignore
from aiocache.base import BaseCache  # type:ignore
from aiocache.serializers import BaseSerializer  # type:ignore
from pydantic import BaseModel
from pydantic.decorator import ValidatedFunction

from .config import Config
from .log import logger

CACHE_ENABLED = Config["cache"]["enabled"].as_bool()
CACHE_DELTA = timedelta(seconds=Config["cache"]["ttl"].as_number())
CACHE_URI = Config["cache"]["uri"].as_str()

T_AsyncFunc = TypeVar("T_AsyncFunc", bound=Callable[..., Coroutine])


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
    endpoint: Callable[..., Coroutine]
    namespace: str
    enabled: bool = True
    ttl: timedelta = CACHE_DELTA

    @staticmethod
    def new(function: Callable[..., Coroutine]):
        return CacheConfig(endpoint=function, namespace=function.__qualname__)


def cache_config(
    enabled: bool = True,
    ttl: timedelta = CACHE_DELTA,
    namespace: Optional[str] = None,
):
    def decorator(endpoint: T_AsyncFunc) -> T_AsyncFunc:
        setattr(
            endpoint,
            "cache_config",
            CacheConfig(
                endpoint=endpoint,
                namespace=namespace or endpoint.__qualname__,
                enabled=enabled,
                ttl=ttl,
            ),
        )
        return endpoint

    return decorator


disable_cache = cache_config(enabled=False)


class CachedValidatedFunction(ValidatedFunction):
    def serialize(self, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> BaseModel:
        values = self.build_values(args=args, kwargs=kwargs)
        return self.model(**values)  # type:ignore


def endpoint_cache(function: T_AsyncFunc) -> T_AsyncFunc:
    from .routing import request_headers, response_headers

    vf = CachedValidatedFunction(function, config={})
    cache: BaseCache = AioCache.from_url(CACHE_URI)  # type:ignore
    config: CacheConfig = getattr(function, "cache_config", CacheConfig.new(function))

    cache.namespace, cache.ttl = config.namespace, config.ttl.total_seconds()
    cache.serializer = GZippedBase85Serializer(encoding="utf-8")

    if not CACHE_ENABLED:
        config.enabled = False

    @wraps(function)
    async def wrapper(*args, **kwargs):
        cache_policy: str = request_headers.get().get("cache-control", "public")

        if (not config.enabled) or (cache_policy.casefold() == "no-store"):
            return await vf.call(*args, **kwargs)

        key = hashlib.md5(
            (model := vf.serialize(args=args, kwargs=kwargs))
            .json(exclude={"self"}, sort_keys=True, ensure_ascii=False)
            .encode()
        ).hexdigest()

        if cache_policy.casefold() == "no-cache":
            await cache.delete(key)

        resp_header = response_headers.get()

        if await cache.exists(key):
            logger.debug(
                f"Request to endpoint <g>{function.__qualname__}</g> "
                f"restoring from <e>{key=}</e> in cache data."
            )
            resp_header.setdefault("X-Cache-Hit", key)
            result, cache_date = await cache.get(key)  # type:ignore
        else:
            result, cache_date = await vf.execute(model), time.time()
            await cache.set(key, (result, cache_date))

        if (cache_remain := int(cache_date + cache.ttl - time.time())) > 0:
            resp_header.setdefault("Cache-Control", f"max-age={cache_remain}")

        return result

    return wrapper  # type:ignore
