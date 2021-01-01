import hashlib
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, overload

from httpx import URL
from pydantic import BaseModel, Extra, Field
from utils.utils import AsyncHTTPClient, BaseNetClient

from .constants import PixivConstants


class UserInfo(BaseModel):
    time: datetime = Field(default_factory=datetime.now)
    access_token: str
    refresh_token: str
    user: Dict[str, Any]

    class Config:
        extra = Extra.allow

    @overload
    @classmethod
    async def login(cls, *, account: Tuple[str, str]) -> "UserInfo":
        ...

    @overload
    @classmethod
    async def login(cls, *, refresh_token: str) -> "UserInfo":
        ...

    @classmethod
    async def login(
        cls,
        *,
        account: Optional[Tuple[str, str]] = None,
        refresh_token: Optional[str] = None,
    ):
        assert (account and refresh_token) is None
        url = URL(PixivConstants.AUTH_HOST + "/auth/token")
        time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        headers = {
            **PixivConstants.DEFAULT_HEADERS,
            "X-Client-Time": time,
            "X-Client-Hash": hashlib.md5(
                time.encode() + PixivConstants.HASH_SECRET.encode()
            ).hexdigest(),
        }
        data = {
            "get_secure_url": 1,
            "client_id": PixivConstants.CLIENT_ID,
            "client_secret": PixivConstants.CLIENT_SECRET,
        }
        if refresh_token:
            data.update({"grant_type": "refresh_token", "refresh_token": refresh_token})
        elif account:
            username, password = account
            data.update(
                {"grant_type": "password", "username": username, "password": password}
            )
        async with AsyncHTTPClient(
            proxies=PixivConstants.CONFIG["proxy"].get(Dict[str, str])  # type:ignore
        ) as client:
            response = await client.post(url, data=data, headers=headers)
            response.raise_for_status()
        return cls.parse_obj(response.json())

    async def renew(self) -> "UserInfo":
        return await self.login(refresh_token=self.refresh_token)


class NetRequest(BaseNetClient):
    def __init__(self, user: UserInfo):
        super().__init__(
            headers=PixivConstants.DEFAULT_HEADERS.copy(),
            proxies=PixivConstants.CONFIG["proxy"].as_dict(),
        )
        self.user = user
        self.headers["accept-language"] = PixivConstants.CONFIG["language"].as_str()
        self.headers["authorization"] = f"Bearer {self.user.access_token}"
