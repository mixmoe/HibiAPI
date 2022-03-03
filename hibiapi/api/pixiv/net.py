import hashlib
from datetime import datetime
from typing import Optional

from httpx import URL
from pydantic import BaseModel, Extra, Field

from hibiapi.utils.net import BaseNetClient

from .constants import PixivConstants


class AccountDataModel(BaseModel):
    class Config:
        extra = Extra.allow


class PixivUserData(AccountDataModel):
    account: str
    id: int
    is_premium: bool
    mail_address: str
    name: str


class PixivAuthData(AccountDataModel):
    time: datetime = Field(default_factory=datetime.now)
    expires_in: int
    access_token: str
    refresh_token: str
    user: PixivUserData


class NetRequest(BaseNetClient):
    _user: Optional[PixivAuthData] = None

    def __init__(self, user: Optional[PixivAuthData] = None):
        super().__init__(
            headers=PixivConstants.DEFAULT_HEADERS.copy(),
            proxies=PixivConstants.CONFIG["proxy"].as_dict(),
        )
        if user is not None:
            self.user = user
        self.headers["accept-language"] = PixivConstants.CONFIG["language"].as_str()

    @property
    def user(self):
        return self._user.copy() if self._user else None

    @user.setter
    def user(self, user: PixivAuthData):
        self._user = user
        self.headers["authorization"] = f"Bearer {user.access_token}"
        self.reset_client()

    async def login(self):
        if self.user is not None:
            self.user = await self.auth(self.user.refresh_token)
        elif token := PixivConstants.CONFIG["account"]["token"].as_str().strip():
            self.user = await self.auth(token)
        else:
            raise ValueError("Pixiv account refresh_token is not configured.")
        return self.user

    async def auth(self, refresh_token: str):
        url = URL(PixivConstants.AUTH_HOST).join("/auth/token")
        time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        headers = {
            **self.headers,
            "X-Client-Time": time,
            "X-Client-Hash": hashlib.md5(
                time.encode() + PixivConstants.HASH_SECRET
            ).hexdigest(),
        }
        payload = {
            "get_secure_url": 1,
            "client_id": PixivConstants.CLIENT_ID,
            "client_secret": PixivConstants.CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        async with self as client:
            response = await client.post(url, data=payload, headers=headers)
            response.raise_for_status()

        return PixivAuthData.parse_obj(response.json())
