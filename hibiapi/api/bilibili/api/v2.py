from collections.abc import Coroutine
from enum import Enum
from functools import wraps
from typing import Callable, Optional, TypeVar

from hibiapi.api.bilibili.api.base import (
    BaseBilibiliEndpoint,
    TimelineType,
    VideoFormatType,
    VideoQualityType,
)
from hibiapi.utils.decorators import enum_auto_doc
from hibiapi.utils.exceptions import ClientSideException
from hibiapi.utils.net import AsyncHTTPClient
from hibiapi.utils.routing import BaseEndpoint

_AnyCallable = TypeVar("_AnyCallable", bound=Callable[..., Coroutine])


def process_keyerror(function: _AnyCallable) -> _AnyCallable:
    @wraps(function)
    async def wrapper(*args, **kwargs):
        try:
            return await function(*args, **kwargs)
        except (KeyError, IndexError) as e:
            raise ClientSideException(detail=str(e)) from None

    return wrapper  # type:ignore


@enum_auto_doc
class SearchType(str, Enum):
    """搜索类型"""

    search = "search"
    """综合搜索"""

    suggest = "suggest"
    """搜索建议"""

    hot = "hot"
    """热门"""


class BilibiliEndpointV2(BaseEndpoint, cache_endpoints=False):
    def __init__(self, client: AsyncHTTPClient):
        super().__init__(client)
        self.base = BaseBilibiliEndpoint(client)

    @process_keyerror
    async def playurl(
        self,
        *,
        aid: int,
        page: Optional[int] = None,
        quality: VideoQualityType = VideoQualityType.VIDEO_480P,
        type: VideoFormatType = VideoFormatType.MP4,
    ):  # NOTE: not completely same with origin
        video_view = await self.base.view(aid=aid)
        if page is None:
            return video_view
        cid: int = video_view["data"]["pages"][page - 1]["cid"]
        return await self.base.playurl(
            aid=aid,
            cid=cid,
            quality=quality,
            type=type,
        )

    async def seasoninfo(self, *, season_id: int):  # NOTE: not same with origin
        return await self.base.season_info(season_id=season_id)

    async def source(self, *, episode_id: int):
        return await self.base.bangumi_source(episode_id=episode_id)

    async def seasonrecommend(self, *, season_id: int):  # NOTE: not same with origin
        return await self.base.season_recommend(season_id=season_id)

    async def search(
        self,
        *,
        keyword: str = "",
        type: SearchType = SearchType.search,
        page: int = 1,
        pagesize: int = 20,
        limit: int = 50,
    ):
        if type == SearchType.suggest:
            return await self.base.search_suggest(keyword=keyword)
        elif type == SearchType.hot:
            return await self.base.search_hot(limit=limit)
        else:
            return await self.base.search(
                keyword=keyword,
                page=page,
                pagesize=pagesize,
            )

    async def timeline(
        self, *, type: TimelineType = TimelineType.GLOBAL
    ):  # NOTE: not same with origin
        return await self.base.timeline(type=type)

    async def space(self, *, vmid: int, page: int = 1, pagesize: int = 10):
        return await self.base.space(
            vmid=vmid,
            page=page,
            pagesize=pagesize,
        )

    async def archive(self, *, vmid: int, page: int = 1, pagesize: int = 10):
        return await self.base.space_archive(
            vmid=vmid,
            page=page,
            pagesize=pagesize,
        )

    async def favlist(self, *, fid: int, vmid: int, page: int = 1, pagesize: int = 20):
        return await self.base.favorite_video(
            fid=fid,
            vmid=vmid,
            page=page,
            pagesize=pagesize,
        )
