import hashlib
from random import randint
from typing import Any, Dict, Optional

from httpx import URL, HTTPError, HTTPStatusError
from utils.exceptions import UpstreamAPIException
from utils.utils import BaseEndpoint


class TiebaEndpoint(BaseEndpoint):
    base = "http://c.tieba.baidu.com"

    def _sign(self, endpoint: str, params: Dict[str, Any]) -> URL:
        def random_digit(length: int) -> str:
            return "".join(map(str, [randint(0, 9) for _ in range(length)]))

        params.update(
            {
                "_client_id": "wappc_" + random_digit(13) + "_" + random_digit(3),
                "_client_type": 2,
                "_client_version": "9.9.8.32",
            }
        )
        params = {k: params[k] for k in sorted(params.keys())}
        url = self._join(self.base, endpoint, params)
        sign = (
            hashlib.md5(url.query.replace(b"&", b"") + b"tiebaclient!!!")
            .hexdigest()
            .upper()
        )
        return URL(url, params={"sign": sign})

    async def request(
        self, endpoint: str, *, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            response = await self.client.post(
                (url := self._sign(endpoint, params or {})),
                content=url.query,
            )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as e:
            raise UpstreamAPIException(detail=e.response.text)
        except HTTPError:
            raise UpstreamAPIException

    async def post_list(self, *, name: str, page: int = 1, size: int = 50):
        return await self.request(
            "c/f/frs/page",
            params={
                "kw": name,
                "pn": page,
                "rn": size,
            },
        )

    async def post_detail(
        self,
        *,
        tid: int,
        page: int = 1,
        size: int = 50,
        reversed: bool = False,
    ):
        return await self.request(
            "c/f/pb/page",
            params={
                **({"last": 1, "r": 1} if reversed else {}),
                "kz": tid,
                "pn": page,
                "rn": size,
            },
        )

    async def subpost_detail(
        self,
        *,
        tid: int,
        pid: int,
        page: int = 1,
        size: int = 50,
    ):
        return await self.request(
            "c/f/pb/floor",
            params={
                "kz": tid,
                "pid": pid,
                "pn": page,
                "rn": size,
            },
        )

    async def user_profile(self, *, uid: int):
        return await self.request(
            "c/u/user/profile",
            params={
                "uid": uid,
                "need_post_count": 1,
                "has_plist": 1,
            },
        )
