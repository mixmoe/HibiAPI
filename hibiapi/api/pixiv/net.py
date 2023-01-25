import asyncio
import hashlib
from datetime import datetime, timedelta, timezone
from itertools import cycle
from typing import Dict, List

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
    def __init__(self, tokens: List[str]):
        super().__init__(
            headers=PixivConstants.DEFAULT_HEADERS.copy(),
            proxies=PixivConstants.CONFIG["proxy"].as_dict(),
        )
        self.user_tokens = cycle(tokens)
        self.auth_lock = asyncio.Lock()
        self.user_tokens_dict: Dict[str, PixivAuthData] = {}
        self.headers["accept-language"] = PixivConstants.CONFIG["language"].as_str()

    def get_available_user(self):
        token = next(self.user_tokens)
        if (auth_data := self.user_tokens_dict.get(token)) and (
            auth_data.time + timedelta(minutes=1, seconds=auth_data.expires_in)
            > datetime.now()
        ):
            return auth_data, token
        return None, token

    async def auth(self, refresh_token: str):
        url = URL(PixivConstants.AUTH_HOST).join("/auth/token")
        time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
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

        self.user_tokens_dict[refresh_token] = PixivAuthData.parse_obj(response.json())
        user_data = self.user_tokens_dict[refresh_token].user
        logger.opt(colors=True).info(
            f"Pixiv account <m>{user_data.id}</m> info <b>Updated</b>: "
            f"<b><e>{user_data.name}</e>({user_data.account})</b>."
        )

        return self.user_tokens_dict[refresh_token]
