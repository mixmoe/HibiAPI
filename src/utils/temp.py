import os
from datetime import datetime, timedelta
from pathlib import Path
from secrets import token_hex
from threading import Lock
from typing import Optional
from urllib.parse import ParseResult

from fastapi import Request

from .config import DATA_PATH, Config
from .decorators import ToAsync


class TempFile:
    path = DATA_PATH / "temp"
    path_depth = 3
    name_length = 16

    _lock = Lock()

    @classmethod
    def create(cls, ext: str = ".tmp") -> Path:
        with cls._lock:
            filename = token_hex(cls.name_length) + ext
            path: Path = cls.path / "/".join(filename[: cls.path_depth]) / filename
            path.parent.mkdir(exist_ok=True, parents=True)
        return path

    @classmethod
    def to_url(cls, request: Request, path: Path) -> str:
        return ParseResult(
            scheme=request.url.scheme,
            netloc=request.url.netloc,
            path=f"/temp/{path.relative_to(cls.path)}",
            params="",
            query="",
            fragment="",
        ).geturl()

    @classmethod
    @ToAsync
    def clean(cls, expiry: Optional[timedelta] = None) -> int:
        expiry = expiry or timedelta(days=Config["data"]["temp-expiry"].get(float))
        now = datetime.now().timestamp()
        removed = 0
        for parent, folders, files in os.walk(cls.path):
            for file in files:
                path = Path(parent) / file
                if (now - path.stat().st_mtime) >= expiry.total_seconds():
                    os.remove(path)
                    removed += 1
            for folder in folders:
                path = Path(parent) / folder
                if not os.listdir(path):
                    path.rmdir()
                    removed += 1
        return removed
