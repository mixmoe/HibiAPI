import asyncio
import hashlib
import random
from datetime import datetime
from itertools import cycle
from typing import Dict, Optional, Union, cast

from httpx import URL
from pydantic import BaseModel, Extra, Field

from hibiapi.utils.log import logger
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
    _users_iter: Optional["cycle[PixivAuthData]"] = None

    def __init__(self):
        super().__init__(
            headers=PixivConstants.DEFAULT_HEADERS.copy(),
            proxies=PixivConstants.CONFIG["proxy"].as_dict(),
        )
        self._users: Dict[int, PixivAuthData] = {}
        self.headers["accept-language"] = PixivConstants.CONFIG["language"].as_str()

    @property
    def user(self):
        return next(self._users_iter, None) if self._users_iter else None

    @user.setter
    def user(self, user: PixivAuthData):
        logger.opt(colors=True).info(
            f"Pixiv account <m>{user.user.id}</m> info <b>Updated</b>: "
            f"<b><e>{user.user.name}</e>({user.user.account})</b>."
        )
        self._users[user.user.id] = user

        users_data = [*self._users.values()]
        random.shuffle(users_data)
        self._users_iter = cycle(users_data)

    async def login(self):
        tokens = [
            token.strip()
            for token in PixivConstants.CONFIG["account"]["token"].as_str_seq()
        ]
        if not tokens:
            raise ValueError("Pixiv account refresh_token is not configured.")

        for result in await asyncio.gather(
            *map(self.auth, tokens), return_exceptions=True
        ):
            result = cast(Union[PixivAuthData, Exception], result)
            if isinstance(result, Exception):
                logger.opt(exception=result).error(
                    "Pixiv account failed to authenticate:"
                )
                continue
            self.user = result

        if not self.user:
            raise ValueError("No available Pixiv account.")

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
