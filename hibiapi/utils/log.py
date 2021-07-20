import logging
import re
import sys
from asyncio.log import logger as _asyncio_logger
from datetime import timedelta
from typing import TYPE_CHECKING

import sentry_sdk.integrations.logging as sentry
from loguru import logger as _logger

from .config import DATA_PATH, Config

if TYPE_CHECKING:
    from loguru import Logger


LOG_PATH = DATA_PATH / "logs"
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_FORMAT = Config["log"]["format"].as_str().strip()
LOG_LEVEL = Config["log"]["level"].get(str).upper()


logger: "Logger" = _logger.opt(colors=True)
logger.remove()
logger.add(
    LOG_PATH / "{time}.log",
    level=LOG_LEVEL,
    encoding="utf-8",
    enqueue=True,
    compression="zip",
    rotation=timedelta(days=1),
)
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    filter=lambda record: record["level"].no < 30,
)
logger.add(sys.stderr, level="WARNING", format=LOG_FORMAT)
logger.add(sentry.BreadcrumbHandler(), level=LOG_LEVEL)
logger.add(sentry.EventHandler(), level="ERROR")
logger.level(LOG_LEVEL)


class LoguruHandler(logging.Handler):
    _tag_escape_re = re.compile(r"</?((?:[fb]g\s)?[^<>\s]*)>")

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type:ignore

        frame, depth, message = logging.currentframe(), 2, record.getMessage()
        while frame.f_code.co_filename == logging.__file__:  # type:ignore
            frame = frame.f_back  # type:ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info, colors=True).log(
            level, ("<e>" + self._escape_tag(message) + "</e>")
        )

    @classmethod
    def _escape_tag(cls, string: str) -> str:
        return cls._tag_escape_re.sub(r"\\\g<0>", string)


_asyncio_logger.handlers.clear()
_asyncio_logger.addHandler(LoguruHandler())

_aiocache_logger = logging.getLogger("aiocache")
_aiocache_logger.handlers.clear()
_aiocache_logger.addHandler(LoguruHandler())
