from __future__ import annotations

import asyncio
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
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from .log import logger

_T = TypeVar("_T")


def TimeIt(function: Callable) -> Callable:
    @wraps(function)
    async def asyncWrapper(*args: Any, **kwargs: Any):
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
    def syncWrapper(*args: Any, **kwargs: Any):
        start = datetime.now()
        try:
            return function(*args, **kwargs)
        finally:
            delta = datetime.now() - start
            logger.trace(
                f"<g>Sync</g> function <y>{function.__qualname__}</y> "
                f"cost <e>{delta.total_seconds() * 1000:.3f}ms</e>"
            )

    return asyncWrapper if iscoroutinefunction(function) else syncWrapper


class RetryT(Protocol):
    @overload
    def __call__(self, function: Callable) -> Callable:
        ...

    @overload
    def __call__(
        self,
        *,
        retries: int = ...,
        delay: float = ...,
        exceptions: Optional[Iterable[Type[Exception]]] = ...,
    ) -> RetryT:
        ...

    def __call__(
        self,
        function: Optional[Callable] = ...,
        *,
        retries: int = ...,
        delay: float = ...,
        exceptions: Optional[Iterable[Type[Exception]]] = ...,
    ) -> Union[Callable, RetryT]:
        ...


@overload
def Retry(function: Callable) -> Callable:
    ...


@overload
def Retry(
    *,
    retries: int = ...,
    delay: float = ...,
    exceptions: Optional[Iterable[Type[Exception]]] = ...,
) -> RetryT:
    ...


def Retry(
    function: Optional[Callable] = None,
    *,
    retries: int = 3,
    delay: float = 0.1,
    exceptions: Optional[Iterable[Type[Exception]]] = None,
) -> Union[Callable, RetryT]:
    if function is None:
        return partial(
            Retry,
            retries=retries,
            delay=delay,
            exceptions=exceptions,
        )

    timed_func = TimeIt(function)
    allowedExceptions: Tuple[Type[Exception], ...] = tuple(exceptions or [Exception])
    assert (retries >= 1) and (delay >= 0)

    @wraps(timed_func)
    def syncWrapper(*args: Any, **kwargs: Any):
        for retried in range(retries):
            try:
                return timed_func(*args, **kwargs)
            except Exception as exception:
                if (remain := retries - retried) <= 0 or (
                    not isinstance(exception, allowedExceptions)
                ):
                    raise
                logger.opt().debug(
                    f"Retry of {timed_func=} trigged "
                    f"due to {exception=} raised ({remain=})"
                )
                syncSleep(delay)

    @wraps(timed_func)
    async def asyncWrapper(*args: Any, **kwargs: Any):
        for retried in range(retries):
            try:
                return await timed_func(*args, **kwargs)
            except Exception as exception:
                if (remain := retries - retried) <= 0 or (
                    not isinstance(exception, allowedExceptions)
                ):
                    raise
                logger.opt().debug(
                    f"Retry of {timed_func=} trigged "
                    f"due to {exception=} raised ({remain=})"
                )
                await asyncSleep(delay)

    return asyncWrapper if iscoroutinefunction(function) else syncWrapper


def ToAsync(function: Callable[..., _T]) -> Callable[..., Coroutine[Any, Any, _T]]:
    @TimeIt
    @wraps(function)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: function(*args, **kwargs)
        )

    return wrapper
