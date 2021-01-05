import os
from datetime import datetime, timedelta
from pathlib import Path
from secrets import token_hex

from .decorators import ToAsync


class TempFile:
    path = Path(".") / "data" / "temp"
    path_depth = 3
    name_length = 16

    @classmethod
    def create(cls, ext: str = ".tmp") -> Path:
        filename = token_hex(cls.name_length) + ext
        path: Path = cls.path / "/".join(filename[: cls.path_depth]) / filename
        path.parent.mkdir(exist_ok=True, parents=True)
        return path

    @classmethod
    @ToAsync
    def clean(cls, expiry: timedelta = timedelta(days=7)) -> int:
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
