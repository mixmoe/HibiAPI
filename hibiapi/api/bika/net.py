import asyncio
from base64 import urlsafe_b64decode
from datetime import datetime, timezone
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

from hibiapi.api.bika.constants import BikaConstants
from hibiapi.utils.net import BaseNetClient

if TYPE_CHECKING:
    from .api import BikaEndpoints


class BikaLogin(BaseModel):
    email: str
    password: str


class JWTHeader(BaseModel):
    alg: str
    typ: Literal["JWT"]


class JWTBody(BaseModel):
    id: str = Field(alias="_id")
    iat: datetime
    exp: datetime


@lru_cache(maxsize=4)
def load_jwt(token: str):
    def b64pad(data: str):
        return data + "=" * (-len(data) % 4)

    head, body, _ = token.split(".")
    head_data = JWTHeader.parse_raw(urlsafe_b64decode(b64pad(head)))
    body_data = JWTBody.parse_raw(urlsafe_b64decode(b64pad(body)))
    return head_data, body_data


class NetRequest(BaseNetClient):
    _token: Optional[str] = None

    def __init__(self):
        super().__init__(
            headers=BikaConstants.DEFAULT_HEADERS.copy(),
            proxies=BikaConstants.CONFIG["proxy"].as_dict(),
        )
        self.auth_lock = asyncio.Lock()

    @property
    def token(self) -> Optional[str]:
        if self._token is None:
            return None
        _, body = load_jwt(self._token)
        return None if body.exp < datetime.now(timezone.utc) else self._token

    async def login(self, endpoint: "BikaEndpoints"):
        login_data = BikaConstants.CONFIG["account"].get(BikaLogin)
        login_result: Dict[str, Any] = await endpoint.request(
            "auth/sign-in",
            body=login_data.dict(),
            no_token=True,
        )
        assert login_result["code"] == 200, login_result["message"]
        if not (
            isinstance(login_data := login_result.get("data"), dict)
            and "token" in login_data
        ):
            raise ValueError("failed to read Bika account token.")
        self._token = login_data["token"]
