import hashlib
import hmac
from datetime import timedelta
from enum import Enum
from time import time
from typing import Any, Dict, Optional, cast

from httpx import URL

from hibiapi.api.bika.constants import BikaConstants
from hibiapi.api.bika.net import NetRequest
from hibiapi.utils.cache import cache_config
from hibiapi.utils.decorators import enum_auto_doc
from hibiapi.utils.net import catch_network_error
from hibiapi.utils.routing import BaseEndpoint, dont_route, request_headers


@enum_auto_doc
class ImageQuality(str, Enum):
    """哔咔API返回的图片质量"""

    low = "low"
    """低质量"""
    medium = "medium"
    """中等质量"""
    high = "high"
    """高质量"""
    original = "original"
    """原图"""


@enum_auto_doc
class ResultSort(str, Enum):
    """哔咔API返回的搜索结果排序方式"""

    date_descending = "dd"
    """最新发布"""
    date_ascending = "da"
    """最早发布"""
    like_descending = "ld"
    """最多喜欢"""
    views_descending = "vd"
    """最多浏览"""


class BikaEndpoints(BaseEndpoint):
    @staticmethod
    def _sign(url: URL, timestamp_bytes: bytes, nonce: bytes, method: bytes):
        return hmac.new(
            BikaConstants.DIGEST_KEY,
            (
                url.raw_path.lstrip(b"/")
                + timestamp_bytes
                + nonce
                + method
                + BikaConstants.API_KEY
            ).lower(),
            hashlib.sha256,
        ).hexdigest()

    @dont_route
    @catch_network_error
    async def request(
        self,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        no_token: bool = False,
    ):
        net_client = cast(NetRequest, self.client.net_client)
        if not no_token:
            async with net_client.auth_lock:
                if net_client.token is None:
                    await net_client.login(self)

        headers = {
            "Authorization": net_client.token or "",
            "Time": (current_time := f"{time():.0f}".encode()),
            "Image-Quality": request_headers.get().get(
                "X-Image-Quality", ImageQuality.medium
            ),
            "Nonce": (nonce := hashlib.md5(current_time).hexdigest().encode()),
            "Signature": self._sign(
                request_url := self._join(
                    base=BikaConstants.API_HOST,
                    endpoint=endpoint,
                    params=params or {},
                ),
                current_time,
                nonce,
                b"GET" if body is None else b"POST",
            ),
        }

        response = await (
            self.client.get(request_url, headers=headers)
            if body is None
            else self.client.post(request_url, headers=headers, json=body)
        )
        return response.json()

    @cache_config(ttl=timedelta(days=1))
    async def collections(self):
        return await self.request("collections")

    @cache_config(ttl=timedelta(days=3))
    async def categories(self):
        return await self.request("categories")

    @cache_config(ttl=timedelta(days=3))
    async def keywords(self):
        return await self.request("keywords")

    async def advanced_search(
        self,
        *,
        keyword: str,
        page: int = 1,
        sort: ResultSort = ResultSort.date_descending,
    ):
        return await self.request(
            "comics/advanced-search",
            body={
                "keyword": keyword,
                "sort": sort,
            },
            params={
                "page": page,
                "s": sort,
            },
        )

    async def category_list(
        self,
        *,
        category: str,
        page: int = 1,
        sort: ResultSort = ResultSort.date_descending,
    ):
        return await self.request(
            "comics",
            params={
                "page": page,
                "c": category,
                "s": sort,
            },
        )

    async def author_list(
        self,
        *,
        author: str,
        page: int = 1,
        sort: ResultSort = ResultSort.date_descending,
    ):
        return await self.request(
            "comics",
            params={
                "page": page,
                "a": author,
                "s": sort,
            },
        )

    @cache_config(ttl=timedelta(days=3))
    async def comic_detail(self, *, id: str):
        return await self.request("comics/{id}", params={"id": id})

    async def comic_recommendation(self, *, id: str):
        return await self.request("comics/{id}/recommendation", params={"id": id})

    async def comic_episodes(self, *, id: str, page: int = 1):
        return await self.request(
            "comics/{id}/eps",
            params={
                "id": id,
                "page": page,
            },
        )

    async def comic_page(self, *, id: str, order: int = 1, page: int = 1):
        return await self.request(
            "comics/{id}/order/{order}/pages",
            params={
                "id": id,
                "order": order,
                "page": page,
            },
        )

    async def comic_comments(self, *, id: str, page: int = 1):
        return await self.request(
            "comics/{id}/comments",
            params={
                "id": id,
                "page": page,
            },
        )

    async def games(self, *, page: int = 1):
        return await self.request("games", params={"page": page})

    @cache_config(ttl=timedelta(days=3))
    async def game_detail(self, *, id: str):
        return await self.request("games/{id}", params={"id": id})
