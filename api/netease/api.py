import base64
import json
from secrets import token_urlsafe
from typing import Any, Dict, Optional

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from httpx import HTTPError, HTTPStatusError
from utils.decorators import ToAsync
from utils.exceptions import UpstreamAPIException
from utils.utils import BaseEndpoint

from .constants import NeteaseConstants


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
        try:
            response = await self.client.post(
                self._join(
                    NeteaseConstants.HOST, endpoint=endpoint, params={"csrf_token": ""}
                ),
                data=await _EncryptUtil.encrypt({**(params or {}), "csrf_token": ""}),
            )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as e:
            raise UpstreamAPIException(detail=e.response.text)
        except HTTPError:
            raise UpstreamAPIException

    async def search(self, keyword: str):
        return await self.request(
            "weapi/cloudsearch/get/web",
            params={"s": keyword, "type": 1, "limit": 30, "offset": 0, "total": True},
        )
