from asyncio import sleep as asyncSleep
from datetime import datetime
from functools import partial, wraps
from inspect import iscoroutinefunction
from time import sleep as syncSleep
from typing import (
    Any,
    Callable,
    Coroutine,
    Iterable,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from starlette.concurrency import run_in_threadpool

from .log import logger

_AnyCallable = TypeVar("_AnyCallable", bound=Callable)
_T = TypeVar("_T")


def TimeIt(function: _AnyCallable) -> _AnyCallable:
    @wraps(function)
    async def asyncWrapper(*args, **kwargs):
        start = datetime.now()
        try:
            return await function(*args, **kwargs)
        finally:
            delta = datetime.now() - start
            logger.trace(
                f"<g>Async</g> function <y>{function.__qualname__}</y> "
                f"cost <e>{delta.total_seconds() * 1000:.3f}ms</e>"
            )

    @wraps(function)
    def syncWrapper(*args, **kwargs):
        start = datetime.now()
        try:
            return function(*args, **kwargs)
        finally:
            delta = datetime.now() - start
            logger.trace(
                f"<g>Sync</g> function <y>{function.__qualname__}</y> "
                f"cost <e>{delta.total_seconds() * 1000:.3f}ms</e>"
            )

    return asyncWrapper if iscoroutinefunction(function) else syncWrapper  # type:ignore


@overload
def Retry(function: _AnyCallable) -> _AnyCallable:
    ...


@overload
def Retry(
    *,
    retries: int = 3,
    delay: float = 0.1,
    exceptions: Optional[Iterable[Type[Exception]]] = None,
) -> Callable[[_AnyCallable], _AnyCallable]:
    ...


def Retry(  # type:ignore
    function: Optional[_AnyCallable] = None,
    *,
    retries: int = 3,
    delay: float = 0.1,
    exceptions: Optional[Tuple[Type[Exception], ...]] = None,
) -> Union[_AnyCallable, Callable[[_AnyCallable], _AnyCallable]]:
    if function is None:
        return partial(
            Retry,
            retries=retries,
            delay=delay,
            exceptions=exceptions,
        )  # type:ignore

    function = TimeIt(function)
    allowedExceptions: Tuple[Type[Exception], ...] = tuple(exceptions or [Exception])
    assert (retries >= 1) and (delay >= 0)

    @wraps(function)
    def syncWrapper(*args, **kwargs):
        for retried in range(retries):
            try:
                return function(*args, **kwargs)
            except Exception as exception:
                if (remain := retries - retried) <= 0 or (
                    not isinstance(exception, allowedExceptions)
                ):
                    raise
                logger.opt().debug(
                    f"Retry of {function=} trigged due to {exception=} raised ({remain=})"
                )
                syncSleep(delay)

    @wraps(function)
    async def asyncWrapper(*args, **kwargs):
        for retried in range(retries):
            try:
                return await function(*args, **kwargs)
            except Exception as exception:
                if (remain := retries - retried) <= 0 or (
                    not isinstance(exception, allowedExceptions)
                ):
                    raise
                logger.opt().debug(
                    f"Retry of {function=} trigged due to {exception=} raised ({remain=})"
                )
                await asyncSleep(delay)

    return asyncWrapper if iscoroutinefunction(function) else syncWrapper  # type:ignore


def ToAsync(function: Callable[..., _T]) -> Callable[..., Coroutine[Any, Any, _T]]:
    @TimeIt
    @wraps(function)
    async def wrapper(*args, **kwargs):
        return await run_in_threadpool(function, *args, **kwargs)

    return wrapper
