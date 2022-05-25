from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import AnyHttpUrl, BaseModel, Extra, Field


class ExceptionReturn(BaseModel):
    url: Optional[AnyHttpUrl] = None
    time: datetime = Field(default_factory=datetime.now)
    code: int = Field(ge=400, le=599)
    detail: str
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
        self.data = ExceptionReturn(
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


class RateLimitReachedException(ClientSideException):
    code = 429
    detail = "Rate limit reached"
