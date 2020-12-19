from typing import Any, Dict, Optional

from fastapi.exceptions import HTTPException


class BaseServerException(HTTPException):
    code: int = 500
    detail: str = "Server Fault"
    headers: Dict[str, Any] = {}

    def __init__(
        self,
        detail: Optional[str] = None,
        *,
        code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        detail = detail or self.detail
        headers = headers or self.headers
        code = code or self.code
        super().__init__(status_code=code, detail=detail, headers=headers)


class ServerSideException(BaseServerException):
    code = 500
    detail = "Internal Server Error"


class UpstreamAPIException(ServerSideException):
    code = 502
    detail = "Upstram API request failed"


class ClientSideException(BaseServerException):
    code = 400
    detail = "Bad Request"
