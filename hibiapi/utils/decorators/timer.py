from __future__ import annotations

import time
from dataclasses import dataclass, field
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, ClassVar, Dict, Optional, TypeVar

from hibiapi.utils.log import logger

Callable_T = TypeVar("Callable_T", bound=Callable)


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

    def __call__(self, function: Callable_T) -> Callable_T:
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

        return (
            async_wrapper if iscoroutinefunction(function) else sync_wrapper
        )  # type:ignore


TimeIt = Timer(logger_func=logger.trace)
