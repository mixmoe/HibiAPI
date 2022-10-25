import logging
import re
import sys
from datetime import timedelta
from pathlib import Path
from typing import Optional

import sentry_sdk.integrations.logging as sentry
from loguru import logger as _logger

from hibiapi.utils.config import Config

LOG_FILE = Config["log"]["file"].get(Optional[Path])
LOG_LEVEL = Config["log"]["level"].as_str().strip().upper()
LOG_FORMAT = Config["log"]["format"].as_str().strip()


class LoguruHandler(logging.Handler):
    _tag_escape_re = re.compile(r"</?((?:[fb]g\s)?[^<>\s]*)>")

    @classmethod
    def escape_tag(cls, string: str) -> str:
        return cls._tag_escape_re.sub(r"\\\g<0>", string)

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth, message = logging.currentframe(), 2, record.getMessage()
        while frame.f_code.co_filename == logging.__file__:  # type: ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info, colors=True).log(
            level, f"<e>{self.escape_tag(message)}</e>"
        )


logger = _logger.opt(colors=True)
logger.remove()
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    filter=lambda record: record["level"].no < logging.WARNING,
)
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    filter=lambda record: record["level"].no >= logging.WARNING,
    format=LOG_FORMAT,
)
logger.add(sentry.BreadcrumbHandler(), level=LOG_LEVEL)
logger.add(sentry.EventHandler(), level="ERROR")

if LOG_FILE is not None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(LOG_FILE),
        level=LOG_LEVEL,
        encoding="utf-8",
        rotation=timedelta(days=1),
    )

logger.level(LOG_LEVEL)
