from pathlib import Path
from tempfile import mkdtemp, mkstemp
from threading import Lock
from urllib.parse import ParseResult

from fastapi import Request


class TempFile:
    path = Path(mkdtemp())
    path_depth = 3
    name_length = 16

    _lock = Lock()

    @classmethod
    def create(cls, ext: str = ".tmp"):
        descriptor, str_path = mkstemp(suffix=ext, dir=str(cls.path))
        return descriptor, Path(str_path)

    @classmethod
    def to_url(cls, request: Request, path: Path) -> str:
        assert cls.path
        return ParseResult(
            scheme=request.url.scheme,
            netloc=request.url.netloc,
            path=f"/temp/{path.relative_to(cls.path)}",
            params="",
            query="",
            fragment="",
        ).geturl()
