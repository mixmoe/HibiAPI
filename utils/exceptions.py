import json
from datetime import datetime
from pathlib import Path
from secrets import token_hex
from typing import Any, Dict, Iterable, Optional, Type

from fastapi.exceptions import HTTPException
from pydantic import BaseModel


class ExceptionStorage:
    EXCEPTION_PATH = Path(".") / "data" / "errors"
    PATH_DEPTH = 3
    ID_LENGTH = 8

    class ExceptionInfo(BaseModel):
        time: datetime
        stamp: float
        id: str
        traceback: str

    @classmethod
    def _resolvePath(cls, id_: str) -> Path:
        assert len(id_) >= cls.PATH_DEPTH
        filename = id_ + ".json"
        path = cls.EXCEPTION_PATH / ("/".join(filename[: cls.PATH_DEPTH])) / filename
        path.parent.mkdir(exist_ok=True, parents=True)
        return path

    @classmethod
    def save(cls, traceback: str, *, time: Optional[datetime] = None) -> str:
        traceID = token_hex(cls.ID_LENGTH).upper()
        time = time or datetime.now()
        traceData = cls.ExceptionInfo(
            time=time, stamp=time.timestamp(), id=traceID, traceback=traceback
        )
        path = cls._resolvePath(traceID)
        path.write_text(
            traceData.json(ensure_ascii=False, indent=4, sort_keys=True),
            encoding="utf-8",
        )
        return traceID

    @classmethod
    def read(cls, id_: str):
        path = cls._resolvePath(id_.upper())
        assert path.exists()
        return cls.ExceptionInfo.parse_obj(json.loads(path.read_text(encoding="utf-8")))


class BaseServerException(HTTPException):
    code: int = 500
    detail: str = "Server Fault"
    headers: Dict[str, Any] = {}

    def __init__(
        self,
        detail: Optional[str] = None,
        *,
        code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
        **params
    ) -> None:
        detail = detail or self.detail
        headers = headers or self.headers
        code = code or self.code
        self.extra = params
        super().__init__(status_code=code, detail=detail, headers=headers)


class ServerSideException(BaseServerException):
    code = 500
    detail = "Internal Server Error"


class UpstreamAPIException(ServerSideException):
    code = 502
    detail = "Upstram API request failed"


class UncaughtException(ServerSideException):
    code = 500
    detail = "Uncaught exception raised during processing"
    exc: Exception


class ClientSideException(BaseServerException):
    code = 400
    detail = "Bad Request"


def _getSubclass(cls: Type[BaseServerException]):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in _getSubclass(c)]
    )


def _getCondintions(l: Iterable[Type[BaseServerException]]):  # noqa:E741
    d: Dict[int, Dict[str, Type[BaseServerException]]] = {}
    for i in l:
        d[i.code] = {**d.get(i.code, {}), i.detail: i}
    return d


ALL_EXCEPTIONS = _getSubclass(BaseServerException)
RESPONSE_CONDITIONS = _getCondintions(ALL_EXCEPTIONS)
