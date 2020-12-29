import logging
import re
import sys
from asyncio.log import logger as _asyncioLogger
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger as _logger

from .config import Config

if TYPE_CHECKING:
    from loguru import Logger

_asyncioLogger.setLevel(40)

LOG_PATH = Path(".") / "data" / "logs"
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_FORMAT = Config["log"]["format"].as_str().strip()
LOG_LEVEL = Config["log"]["level"].as_str().upper()


logger: "Logger" = _logger.opt(colors=True)
logger.remove()
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    filter=lambda record: record["level"].no < 30,
)
logger.add(sys.stderr, level="WARNING", format=LOG_FORMAT)
logger.add(
    LOG_PATH / "{time}.log",
    level=LOG_LEVEL,
    encoding="utf-8",
    enqueue=True,
    compression="zip",
    rotation=timedelta(days=1),
)
logger.level(Config["log"]["level"].as_str().upper())


class LoguruHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type:ignore

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type:ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info, colors=True).log(
            level, ("<e>" + self._escape_tag(record.getMessage()) + "</e>")
        )

    @staticmethod
    def _escape_tag(s: str) -> str:
        return re.sub(r"</?((?:[fb]g\s)?[^<>\s]*)>", r"\\\g<0>", s)
