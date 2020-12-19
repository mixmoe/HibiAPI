import hashlib
from datetime import datetime
from http.cookiejar import CookieJar
from threading import current_thread
from typing import Any, Dict, Optional, Tuple, overload

from httpx import URL, AsyncClient, HTTPError
from pydantic import BaseModel, Extra, Field
from utils.decorators import Retry
from utils.exceptions import UpstreamAPIException

from .constants import PixivConstants


class AsyncPixivClient(AsyncClient):
    @Retry
    async def request(self, *args, **kwargs):
        try:
            return await super().request(*args, **kwargs)
        except HTTPError:
            raise UpstreamAPIException


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
        async with AsyncPixivClient(
            proxies=PixivConstants.CONFIG["proxy"].as_dict()
        ) as client:
            response = await client.post(url, data=data, headers=headers)
            response.raise_for_status()
        return cls.parse_obj(response.json())

    async def renew(self) -> "UserInfo":
        return await self.login(refresh_token=self.refresh_token)


class NetRequest:
    def __init__(self, user: UserInfo):
        self.clients: Dict[int, AsyncClient] = {}
        self.user = user
        self.headers = PixivConstants.DEFAULT_HEADERS.copy()
        self.headers["accept-language"] = PixivConstants.CONFIG["language"].as_str()
        self.headers["authorization"] = f"Bearer {self.user.access_token}"
        self.cookies = CookieJar()

    async def __aenter__(self) -> AsyncPixivClient:
        tid = current_thread().ident or 1
        if tid not in self.clients:
            self.clients[tid] = AsyncPixivClient(
                headers=self.headers,
                cookies=self.cookies,
                proxies=PixivConstants.CONFIG["proxy"].as_dict(),
            )
        return await self.clients[tid].__aenter__()  # type:ignore

    async def __aexit__(self, *args):
        tid = current_thread().ident or 1
        if tid not in self.clients:
            return
        return await self.clients[tid].__aexit__(*args)
