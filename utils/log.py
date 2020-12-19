import sys
from asyncio.log import logger as _asyncioLogger
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

logger: "Logger" = _logger.opt(colors=True)
logger.remove()
logger.add(sys.stdout, format=LOG_FORMAT, filter=lambda record: record["level"].no < 30)
logger.add(sys.stderr, level="WARNING", format=LOG_FORMAT)
logger.add(str(LOG_PATH / "{time}.log"), encoding="utf-8", enqueue=True)
logger.level(Config["log"]["level"].as_str().upper())
