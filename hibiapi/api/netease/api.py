import base64
import json
import secrets
import string
from datetime import timedelta
from enum import IntEnum
from ipaddress import IPv4Address
from random import randint
from typing import Any, Dict, List, Optional

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from fastapi import Query

from hibiapi.api.netease.constants import NeteaseConstants
from hibiapi.utils.cache import cache_config
from hibiapi.utils.decorators import enum_auto_doc
from hibiapi.utils.exceptions import UpstreamAPIException
from hibiapi.utils.net import catch_network_error
from hibiapi.utils.routing import BaseEndpoint, dont_route


@enum_auto_doc
class SearchType(IntEnum):
    """搜索内容类型"""

    SONG = 1
    """单曲"""
    ALBUM = 10
    """专辑"""
    ARTIST = 100
    """歌手"""
    PLAYLIST = 1000
    """歌单"""
    USER = 1002
    """用户"""
    MV = 1004
    """MV"""
    LYRICS = 1006
    """歌词"""
    DJ = 1009
    """主播电台"""
    VIDEO = 1014
    """视频"""


@enum_auto_doc
class BitRateType(IntEnum):
    """歌曲码率"""

    LOW = 64000
    MEDIUM = 128000
    STANDARD = 198000
    HIGH = 320000


@enum_auto_doc
class RecordPeriodType(IntEnum):
    """听歌记录时段类型"""

    WEEKLY = 1
    """本周"""
    ALL = 0
    """所有时段"""


class _EncryptUtil:
    alphabets = bytearray(ord(char) for char in string.ascii_letters + string.digits)

    @staticmethod
    def _aes(data: bytes, key: bytes) -> bytes:
        data = pad(data, 16) if len(data) % 16 else data
        return base64.encodebytes(
            AES.new(
                key=key,
                mode=AES.MODE_CBC,
                iv=NeteaseConstants.AES_IV,
            ).encrypt(data)
        )

    @staticmethod
    def _rsa(data: bytes):
        result = pow(
            base=int(data.hex(), 16),
            exp=NeteaseConstants.RSA_PUBKEY,
            mod=NeteaseConstants.RSA_MODULUS,
        )
        return f"{result:0>256x}"

    @classmethod
    def encrypt(cls, data: Dict[str, Any]) -> Dict[str, str]:
        secret = bytes(secrets.choice(cls.alphabets) for _ in range(16))
        secure_key = cls._rsa(bytes(reversed(secret)))
        return {
            "params": cls._aes(
                data=cls._aes(
                    data=json.dumps(data).encode(),
                    key=NeteaseConstants.AES_KEY,
                ),
                key=secret,
            ).decode("ascii"),
            "encSecKey": secure_key,
        }


class NeteaseEndpoint(BaseEndpoint):
    def _construct_headers(self):
        headers = self.client.headers.copy()
        headers["X-Real-IP"] = str(
            IPv4Address(
                randint(
                    int(NeteaseConstants.SOURCE_IP_SEGMENT.network_address),
                    int(NeteaseConstants.SOURCE_IP_SEGMENT.broadcast_address),
                )
            )
        )
        return headers

    @dont_route
    @catch_network_error
    async def request(
        self, endpoint: str, *, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        params = {
            **(params or {}),
            "csrf_token": self.client.cookies.get("__csrf", ""),
        }
        response = await self.client.post(
            self._join(
                NeteaseConstants.HOST,
                endpoint=endpoint,
                params=params,
            ),
            headers=self._construct_headers(),
            data=_EncryptUtil.encrypt(params),
        )
        response.raise_for_status()
        if not response.text.strip():
            raise UpstreamAPIException(
                f"Upstream API {endpoint=} returns blank content"
            )
        return response.json()

    async def search(
        self,
        *,
        s: str,
        search_type: SearchType = SearchType.SONG,
        limit: int = 20,
        offset: int = 0,
    ):
        return await self.request(
            "api/cloudsearch/pc",
            params={
                "s": s,
                "type": search_type,
                "limit": limit,
                "offset": offset,
                "total": True,
            },
        )

    async def artist(self, *, id: int):
        return await self.request(
            "weapi/v1/artist/{artist_id}",
            params={
                "artist_id": id,
            },
        )

    async def album(self, *, id: int):
        return await self.request(
            "weapi/v1/album/{album_id}",
            params={
                "album_id": id,
            },
        )

    async def detail(self, *, id: List[int] = Query()):
        return await self.request(
            "weapi/v3/song/detail",
            params={
                "c": json.dumps(
                    [{"id": str(i)} for i in id],
                ),
            },
        )

    @cache_config(ttl=timedelta(minutes=20))
    async def song(
        self,
        *,
        id: List[int] = Query(),
        br: BitRateType = BitRateType.STANDARD,
    ):
        return await self.request(
            "weapi/song/enhance/player/url",
            params={
                "ids": [str(i) for i in id],
                "br": br,
            },
        )

    async def playlist(self, *, id: int):
        return await self.request(
            "weapi/v6/playlist/detail",
            params={
                "id": id,
                "total": True,
                "offset": 0,
                "limit": 1000,
                "n": 1000,
            },
        )

    async def lyric(self, *, id: int):
        return await self.request(
            "weapi/song/lyric",
            params={
                "id": id,
                "os": "pc",
                "lv": -1,
                "kv": -1,
                "tv": -1,
            },
        )

    async def mv(self, *, id: int):
        return await self.request(
            "api/v1/mv/detail",
            params={
                "id": id,
            },
        )

    async def comments(self, *, id: int, offset: int = 0, limit: int = 1):
        return await self.request(
            "weapi/v1/resource/comments/R_SO_4_{song_id}",
            params={
                "song_id": id,
                "offset": offset,
                "total": True,
                "limit": limit,
            },
        )

    async def record(self, *, id: int, period: RecordPeriodType = RecordPeriodType.ALL):
        return await self.request(
            "weapi/v1/play/record",
            params={
                "uid": id,
                "type": period,
            },
        )

    async def djradio(self, *, id: int):
        return await self.request(
            "api/djradio/v2/get",
            params={
                "id": id,
            },
        )

    async def dj(self, *, id: int, offset: int = 0, limit: int = 20, asc: bool = False):
        # NOTE: Possible not same with origin
        return await self.request(
            "weapi/dj/program/byradio",
            params={
                "radioId": id,
                "offset": offset,
                "limit": limit,
                "asc": asc,
            },
        )

    async def detail_dj(self, *, id: int):
        return await self.request(
            "api/dj/program/detail",
            params={
                "id": id,
            },
        )

    async def user(self, *, id: int):
        return await self.request(
            "weapi/v1/user/detail/{id}",
            params={"id": id},
        )

    async def user_playlist(self, *, id: int, limit: int = 50, offset: int = 0):
        return await self.request(
            "weapi/user/playlist",
            params={
                "uid": id,
                "limit": limit,
                "offset": offset,
            },
        )
