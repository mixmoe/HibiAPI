from asyncio import sleep as asyncSleep
from datetime import datetime
from functools import partial, wraps
from inspect import iscoroutinefunction
from time import sleep as syncSleep
from typing import Callable, Iterable, Optional, Tuple, Type, TypeVar, Union, overload

from .log import logger

_AnyCallable = TypeVar("_AnyCallable", bound=Callable)


def TimeIt(function: _AnyCallable) -> _AnyCallable:
    @wraps(function)
    async def asyncWrapper(*args, **kwargs):
        start = datetime.now()
        try:
            return await function(*args, **kwargs)
        finally:
            delta = datetime.now() - start
            logger.trace(
                f"Async function <y>{function.__name__}</y> "
                f"cost <e>{delta.seconds}s{(delta.microseconds)}ms</e>"
            )

    @wraps(function)
    def syncWrapper(*args, **kwargs):
        start = datetime.now()
        try:
            return function(*args, **kwargs)
        finally:
            delta = datetime.now() - start
            logger.trace(
                f"Sync function <y>{function.__name__}</y> "
                f"cost <e>{delta.seconds}s{(delta.microseconds)}ms</e>"
            )

    return asyncWrapper if iscoroutinefunction(function) else syncWrapper  # type:ignore


@overload
def Retry(function: _AnyCallable) -> _AnyCallable:
    ...


@overload
def Retry(
    *,
    retires: int = 3,
    delay: int = 3,
    exceptions: Optional[Iterable[Type[Exception]]] = None,
) -> Callable[[_AnyCallable], _AnyCallable]:
    ...


def Retry(  # type:ignore
    function: Optional[_AnyCallable] = None,
    *,
    retires: int = 3,
    delay: float = 0.1,
    exceptions: Optional[Tuple[Type[Exception], ...]] = None,
) -> Union[_AnyCallable, Callable[[_AnyCallable], _AnyCallable]]:
    if function is None:
        return partial(Retry, retires=retires, delay=delay, exceptions=exceptions)

    allowedExceptions: Tuple[Type[Exception], ...] = tuple(exceptions or [Exception])
    assert (retires >= 1) and (delay >= 0)

    @wraps(function)
    def syncWrapper(*args, **kwargs):
        exception: Optional[Exception] = None
        for retried in range(retires):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                if not isinstance(e, allowedExceptions):
                    raise
                exception = e
                syncSleep(delay)
                continue
        raise exception  # type:ignore

    @wraps(function)
    async def asyncWrapper(*args, **kwargs):
        exception: Optional[Exception] = None
        for retried in range(retires):
            try:
                return await function(*args, **kwargs)
            except Exception as e:
                if not isinstance(e, allowedExceptions):
                    raise
                exception = e
                await asyncSleep(delay)
                continue
        raise exception  # type:ignore

    return asyncWrapper if iscoroutinefunction(function) else syncWrapper  # type:ignore