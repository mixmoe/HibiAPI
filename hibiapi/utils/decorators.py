from __future__ import annotations

import asyncio
import time
from asyncio import sleep as async_sleep
from dataclasses import dataclass, field
from functools import partial, wraps
from inspect import iscoroutinefunction
from time import sleep as sync_sleep
from typing import (
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
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


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


@dataclass
class Timer:
    """Time your code using a class, context manager, or decorator"""

    timers: ClassVar[Dict[str, float]] = dict()
    name: Optional[str] = None
    text: str = "Elapsed time: {:0.3f} seconds"
    logger_func: Optional[Callable[[str], None]] = print
    _start_time: Optional[float] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialization: add timer to dict of timers"""
        if self.name:
            self.timers.setdefault(self.name, 0)

    def start(self) -> None:
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError("Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError("Timer is not running. Use .start() to start it")

        # Calculate elapsed time
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

        # Report elapsed time
        if self.logger_func:
            self.logger_func(self.text.format(elapsed_time * 1000))
        if self.name:
            self.timers[self.name] += elapsed_time

        return elapsed_time

    def __enter__(self) -> Timer:
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Stop the context manager timer"""
        self.stop()

    def _recreate_cm(self) -> Timer:
        return self.__class__(self.name, self.text, self.logger_func)

    def __call__(self, function: Callable) -> Callable:
        @wraps(function)
        async def async_wrapper(*args: Any, **kwargs: Any):
            self.text = (
                f"<g>Async</g> function <y>{function.__qualname__}</y> "
                "cost <e>{:.3f}ms</e>"
            )

            with self._recreate_cm():
                return await function(*args, **kwargs)

        @wraps(function)
        def sync_wrapper(*args: Any, **kwargs: Any):
            self.text = (
                f"<g>sync</g> function <y>{function.__qualname__}</y> "
                "cost <e>{:.3f}ms</e>"
            )

            with self._recreate_cm():
                return function(*args, **kwargs)

        return async_wrapper if iscoroutinefunction(function) else sync_wrapper


TimeIt = Timer(logger_func=logger.trace)


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
        for retried in range(retries):
            try:
                return timed_func(*args, **kwargs)
            except Exception as exception:
                if (remain := retries - retried) <= 0 or (
                    not isinstance(exception, allowed_exceptions)
                ):
                    raise
                logger.opt().debug(
                    f"Retry of {timed_func=} trigged "
                    f"due to {exception=} raised ({remain=})"
                )
                sync_sleep(delay)

    @wraps(timed_func)
    async def async_wrapper(*args: Any, **kwargs: Any):
        for retried in range(retries):
            try:
                return await timed_func(*args, **kwargs)
            except Exception as exception:
                if (remain := retries - retried) <= 0 or (
                    not isinstance(exception, allowed_exceptions)
                ):
                    raise
                logger.opt().debug(
                    f"Retry of {timed_func=} trigged "
                    f"due to {exception=} raised ({remain=})"
                )
                await async_sleep(delay)

    return async_wrapper if iscoroutinefunction(function) else sync_wrapper


def ToAsync(function: Callable[..., _T]) -> Callable[..., Coroutine[Any, Any, _T]]:
    @TimeIt
    @wraps(function)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: function(*args, **kwargs)
        )

    return wrapper
