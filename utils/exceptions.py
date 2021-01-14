from datetime import datetime
from pathlib import Path
from secrets import token_hex
from traceback import format_tb
from types import TracebackType
from typing import Any, Dict, List, Optional

from pydantic import AnyHttpUrl, BaseModel, Extra, Field, Protocol, conint, constr

from .config import DATA_PATH

EXCEPTION_PATH = DATA_PATH / "errors"
EXCEPTION_PATH_DEPTH = 3
TRACE_ID_LENGTH = 8

TraceIDType = constr(
    strict=True,
    min_length=TRACE_ID_LENGTH * 2,
    max_length=TRACE_ID_LENGTH * 2,
)


class ExceptionInfo(BaseModel):
    time: datetime
    stamp: float
    id: TraceIDType  # type:ignore
    traceback: List[str]

    @staticmethod
    def _resolve_path(id_: str) -> Path:
        assert len(id_) >= EXCEPTION_PATH_DEPTH
        path = EXCEPTION_PATH / ("/".join(id_[:EXCEPTION_PATH_DEPTH])) / (id_ + ".json")
        path.parent.mkdir(exist_ok=True, parents=True)
        return path

    @classmethod
    def new(cls, traceback: Optional[TracebackType] = None):
        traceID = token_hex(TRACE_ID_LENGTH).upper()
        time = datetime.now()
        return cls(
            time=time,
            stamp=time.timestamp(),
            id=traceID,
            traceback=format_tb(traceback),
        )

    @classmethod
    def read(cls, id_: str):
        path = cls._resolve_path(id_)
        assert path.exists()
        return cls.parse_file(path, proto=Protocol.json, encoding="utf-8")

    def persist(self):
        self._resolve_path(self.id).write_text(self.json(), encoding="utf-8")
        return self


class ExceptionReturn(BaseModel):
    url: Optional[AnyHttpUrl] = None
    time: datetime = Field(default_factory=datetime.now)
    code: conint(ge=400, lt=600)  # type:ignore
    detail: str
    trace: Optional[TraceIDType] = None  # type:ignore
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
