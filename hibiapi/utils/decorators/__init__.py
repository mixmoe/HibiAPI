from __future__ import annotations

import asyncio
from asyncio import sleep as async_sleep
from functools import partial, wraps
from inspect import iscoroutinefunction
from time import sleep as sync_sleep
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

from ..log import logger
from .timer import TimeIt

_T = TypeVar("_T")


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
    allowed_exceptions: Tuple[Type[Exception], ...] = tuple(exceptions or [Exception])
    assert (retries >= 1) and (delay >= 0)

    @wraps(timed_func)
    def sync_wrapper(*args: Any, **kwargs: Any):
        error: Optional[Exception] = None
        for retried in range(retries):
            try:
                return timed_func(*args, **kwargs)
            except Exception as exception:
                error = exception
                if not isinstance(exception, allowed_exceptions):
                    raise
                logger.opt().debug(
                    f"Retry of {timed_func=} trigged "
                    f"due to {exception=} raised ({retried=}/{retries=})"
                )
                sync_sleep(delay)
        assert isinstance(error, Exception)
        raise error

    @wraps(timed_func)
    async def async_wrapper(*args: Any, **kwargs: Any):
        error: Optional[Exception] = None
        for retried in range(retries):
            try:
                return await timed_func(*args, **kwargs)
            except Exception as exception:
                error = exception
                if not isinstance(exception, allowed_exceptions):
                    raise
                logger.opt().debug(
                    f"Retry of {timed_func=} trigged "
                    f"due to {exception=} raised ({retried=}/{retries})"
                )
                await async_sleep(delay)
        assert isinstance(error, Exception)
        raise error

    return async_wrapper if iscoroutinefunction(function) else sync_wrapper


def ToAsync(function: Callable[..., _T]) -> Callable[..., Coroutine[Any, Any, _T]]:
    @TimeIt
    @wraps(function)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: function(*args, **kwargs)
        )

    return wrapper
