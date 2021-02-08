import base64
import json
from enum import Enum, IntEnum
from secrets import token_urlsafe
from typing import Any, Dict, Optional

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from utils.decorators import ToAsync
from utils.net import catch_network_error
from utils.routing import BaseEndpoint

from .constants import NeteaseConstants


class EndpointsType(str, Enum):
    search = "search"
    artist = "artist"
    album = "album"
    detail = "detail"
    song = "song"
    playlist = "playlist"
    lyric = "lyric"
    mv = "mv"
    comments = "comments"
    record = "record"
    djradio = "djradio"
    dj = "dj"
    detail_dj = "detail_dj"


class SearchType(IntEnum):
    """
    搜索内容类型

    | **数值** | **含义** |
    |---|---|
    | 1  | 单曲 |
    | 10  | 专辑 |
    | 100  | 歌手 |
    | 1000  | 歌单 |
    | 1002  | 用户 |
    | 1004  | mv |
    | 1006  | 歌词 |
    | 1009  | 主播电台 |
    """

    SONG = 1
    ALBUM = 10
    ARTIST = 100
    PLAYLIST = 1000
    USER = 1002
    MV = 1004
    LYRICS = 1006
    DJ = 1009
    VIDEO = 1014


class BitRateType(IntEnum):
    """
    歌曲码率
    """

    LOW = 64000
    MEDIUM = 128000
    STANDARD = 198000
    HIGH = 320000


class RecordPeriodType(IntEnum):
    """
    听歌记录时段类型

    | **数值** | **含义** |
    |---|---|
    | 0 | 所有时段 |
    | 1 | 本周 |
    """

    WEEKLY = 1
    ALL = 0


class _EncryptUtil:
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
    @ToAsync
    def encrypt(cls, data: Dict[str, Any]) -> Dict[str, str]:
        secret = token_urlsafe(12).encode()
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
    @catch_network_error
    async def request(
        self, endpoint: str, *, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        params = {**(params or {}), "csrf_token": ""}
        response = await self.client.post(
            self._join(
                NeteaseConstants.HOST,
                endpoint=endpoint,
                params=params,
            ),
            data=await _EncryptUtil.encrypt(params),
        )
        response.raise_for_status()
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
            "weapi/cloudsearch/get/web",
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

    async def detail(self, *, id: int):
        return await self.request(
            "weapi/v3/song/detail",
            params={
                "c": json.dumps(
                    [{"id": str(id)}],
                ),
            },
        )

    async def song(self, *, id: int, br: BitRateType = BitRateType.STANDARD):
        return await self.request(
            "weapi/song/enhance/player/url",
            params={
                "ids": [id],
                "br": br,
            },
        )

    async def playlist(self, *, id: int):
        return await self.request(
            "weapi/v3/playlist/detail",
            params={
                "id": id,
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
