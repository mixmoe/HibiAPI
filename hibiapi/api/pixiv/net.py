import hashlib
from datetime import datetime
from typing import Dict, Optional

from httpx import URL
from pydantic import BaseModel, Extra, Field

from hibiapi.utils.net import AsyncHTTPClient, BaseNetClient

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

    @classmethod
    async def login(cls, *, refresh_token: str):
        url = URL(PixivConstants.AUTH_HOST).join("/auth/token")
        time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        headers = {
            **PixivConstants.DEFAULT_HEADERS,
            "X-Client-Time": time,
            "X-Client-Hash": hashlib.md5(
                time.encode() + PixivConstants.HASH_SECRET
            ).hexdigest(),
        }
        data = {
            "get_secure_url": 1,
            "client_id": PixivConstants.CLIENT_ID,
            "client_secret": PixivConstants.CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        async with AsyncHTTPClient(
            proxies=PixivConstants.CONFIG["proxy"].get(Dict[str, str])  # type:ignore
        ) as client:
            response = await client.post(url, data=data, headers=headers)
            response.raise_for_status()
        return cls.parse_obj(response.json())

    async def renew(self) -> "PixivAuthData":
        return await self.login(refresh_token=self.refresh_token)


class NetRequest(BaseNetClient):
    _user: PixivAuthData

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
        return self._user.copy()

    @user.setter
    def user(self, user: PixivAuthData):
        self._user = user
        self.headers["authorization"] = f"Bearer {self.user.access_token}"

    async def login(self):
        if refresh_token := PixivConstants.CONFIG["account"]["token"].as_str().strip():
            self.user = await PixivAuthData.login(refresh_token=refresh_token)
        else:
            raise ValueError("Pixiv account refresh_token is not configured.")

        return self.user
