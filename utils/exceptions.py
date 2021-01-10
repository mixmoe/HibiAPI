import json
from datetime import datetime
from pathlib import Path
from secrets import token_hex
from traceback import format_tb
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra, HttpUrl, conint, constr


class ExceptionStorage:
    EXCEPTION_PATH = Path(".") / "data" / "errors"
    PATH_DEPTH = 3
    ID_LENGTH = 8

    class ExceptionInfo(BaseModel):
        time: datetime
        stamp: float
        id: str
        traceback: List[str]

    @classmethod
    def _resolvePath(cls, id_: str) -> Path:
        assert len(id_) >= cls.PATH_DEPTH
        filename = id_ + ".json"
        path = cls.EXCEPTION_PATH / ("/".join(filename[: cls.PATH_DEPTH])) / filename
        path.parent.mkdir(exist_ok=True, parents=True)
        return path

    @classmethod
    def save(
        cls, traceback: Optional[Any] = None, *, time: Optional[datetime] = None
    ) -> str:
        traceID = token_hex(cls.ID_LENGTH).upper()
        time = time or datetime.now()
        traceData = cls.ExceptionInfo(
            time=time,
            stamp=time.timestamp(),
            id=traceID,
            traceback=format_tb(traceback),
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


class ExceptionReturn(BaseModel):
    url: Optional[HttpUrl] = None
    code: conint(ge=400, lt=600)  # type:ignore
    detail: str
    trace: Optional[  # type:ignore
        constr(
            strict=True,
            min_length=ExceptionStorage.ID_LENGTH * 2,
            max_length=ExceptionStorage.ID_LENGTH * 2,
        )  # type:ignore
    ] = None
    headers: Dict[str, str] = {}

    class Config:
        extra = Extra.allow


class BaseServerException(Exception):
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
        self.data = ExceptionReturn(  # type:ignore
            detail=detail or self.__class__.detail,
            code=code or self.__class__.code,
            headers=headers or self.__class__.headers,
            **params
        )
        super().__init__(detail)


class BaseHTTPException(BaseServerException):
    pass


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

    @classmethod
    def with_exception(cls, e: Exception):
        c = cls(e.__class__.__qualname__)
        c.exc = e
        return c


class ClientSideException(BaseServerException):
    code = 400
    detail = "Bad Request"


class ValidationException(ClientSideException):
    code = 422
