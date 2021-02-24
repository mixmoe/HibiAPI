import hashlib
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple, TypeVar

from aiocache import Cache as AioCache
from aiocache.base import BaseCache
from pydantic import BaseModel
from pydantic.decorator import ValidatedFunction

from .log import logger

_AsyncCallable = TypeVar("_AsyncCallable", bound=Callable[..., Coroutine])


class CacheConfig(BaseModel):
    endpoint: Callable[..., Coroutine]
    namespace: str
    enabled: bool = True
    ttl: timedelta = timedelta(hours=1)
    refresh_key: Optional[str] = None

    @staticmethod
    def new(function: Callable[..., Coroutine]):
        return CacheConfig(endpoint=function, namespace=function.__qualname__)


def cache_config(
    enabled: bool = True,
    ttl: timedelta = timedelta(hours=1),
    refresh_key: Optional[str] = None,
    namespace: Optional[str] = None,
):
    def decorator(endpoint: _AsyncCallable) -> _AsyncCallable:
        setattr(
            endpoint,
            "cache_config",
            CacheConfig(
                endpoint=endpoint,
                namespace=namespace or endpoint.__qualname__,
                enabled=enabled,
                ttl=ttl,
                refresh_key=refresh_key,
            ),
        )
        return endpoint

    return decorator


disable_cache = cache_config(enabled=False)


class CachedValidatedFunction(ValidatedFunction):
    def serialize(self, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> BaseModel:
        values = self.build_values(args=args, kwargs=kwargs)
        return self.model(**values)


def endpoint_cache(function: _AsyncCallable) -> _AsyncCallable:
    vf = CachedValidatedFunction(function)
    cache: BaseCache = AioCache.from_url("memory://")  # type:ignore
    config: CacheConfig = getattr(function, "cache_config", CacheConfig.new(function))

    cache.namespace, cache.ttl = config.namespace, config.ttl.total_seconds()

    @wraps(function)
    async def wrapper(*args, **kwargs):
        if not config.enabled:
            return await vf.call(*args, **kwargs)

        key = hashlib.md5(
            (model := vf.serialize(args=args, kwargs=kwargs))
            .json(exclude={"self"}, sort_keys=True, ensure_ascii=False)
            .encode()
        ).hexdigest()

        if model.dict().get(config.refresh_key or "", False):
            await cache.delete(key)

        if await cache.exists(key):
            logger.debug(
                f"Request to endpoint <g>{function.__qualname__}</g> "
                f"restoring from <e>{key=}</e> in cache data."
            )
            return await cache.get(key)

        await cache.set(key, result := await vf.execute(model))
        return result

    return wrapper  # type:ignore
