import base64
import json
from enum import IntEnum
from secrets import token_urlsafe
from typing import Any, Dict, Optional

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from httpx import HTTPError, HTTPStatusError
from utils.decorators import ToAsync
from utils.exceptions import UpstreamAPIException
from utils.utils import BaseEndpoint

from .constants import NeteaseConstants


class SearchType(IntEnum):
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
    STANDARD = 96000
    HIGH = 320000
    LOSELESS = 3200000


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
    async def request(
        self, endpoint: str, *, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        params = {**(params or {}), "csrf_token": ""}
        try:
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
        except HTTPStatusError as e:
            raise UpstreamAPIException(detail=e.response.text)
        except HTTPError:
            raise UpstreamAPIException

    async def search(
        self,
        *,
        keyword: str,
        type: SearchType = SearchType.SONG,
        limit: int = 30,
        offset: int = 0,
    ):
        return await self.request(
            "weapi/cloudsearch/get/web",
            params={
                "s": keyword,
                "type": type,
                "limit": limit,
                "offset": offset,
                "total": True,
            },
        )

    async def artist(self, *, artist_id: int):
        return await self.request(
            "weapi/v1/artist/{artist_id}",
            params={
                "artist_id": artist_id,
            },
        )

    async def album(self, *, album_id: int):
        return await self.request(
            "music.163.com/weapi/v1/album/{album_id}",
            params={
                "album_id": album_id,
            },
        )

    async def detail(self, *, song_id: int):
        return await self.request(
            "weapi/v3/song/detail",
            params={
                "c": [{"id": song_id}],
            },
        )

    async def url(self, *, song_id: int, bitrate: BitRateType = BitRateType.STANDARD):
        return await self.request(
            "weapi/song/enhance/player/url",
            params={
                "ids": song_id,
                "br": bitrate,
            },
        )

    async def playlist(self, *, playlist_id: int):
        return await self.request(
            "weapi/v3/playlist/detail",
            params={
                "id": playlist_id,
                "n": 1000,
            },
        )

    async def lyric(self, *, song_id: int):
        return await self.request(
            "weapi/song/lyric",
            params={
                "id": song_id,
                "os": "pc",
                "lv": -1,
                "kv": -1,
                "tv": -1,
            },
        )

    async def mv(self, *, mv_id: int):
        return await self.request(
            "weapi/mv/detail",
            params={
                "id": mv_id,
            },
        )
