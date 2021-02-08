from enum import Enum
from functools import wraps
from typing import Callable, Coroutine, Optional, TypeVar, Union

from utils.exceptions import ClientSideException
from utils.net import AsyncHTTPClient
from utils.routing import BaseEndpoint

from .base import (
    BaseBilibiliEndpoint,
    CommentSortType,
    CommentType,
    RankBangumiType,
    RankContentType,
    RankDurationType,
    TimelineType,
    VideoFormatType,
    VideoQualityType,
)

_AnyCallable = TypeVar("_AnyCallable", bound=Callable[..., Coroutine])


def process_keyerror(function: _AnyCallable) -> _AnyCallable:
    @wraps(function)
    async def wrapper(*args, **kwargs):
        try:
            return await function(*args, **kwargs)
        except KeyError as e:
            raise ClientSideException(detail=str(e)) from None

    return wrapper  # type:ignore


class V2EndpointsType(str, Enum):
    playurl = "playurl"
    seasoninfo = "seasoninfo"
    source = "source"
    seasonrecommend = "seasonrecommend"
    comments = "comments"
    search = "search"
    rank = "rank"
    typedynamic = "typedynamic"
    recommend = "recommend"
    timeline = "timeline"
    space = "space"
    archive = "archive"
    favlist = "favlist"


class SearchType(str, Enum):
    search = "search"
    suggest = "suggest"
    hot = "hot"


class BilibiliEndpointV2(BaseEndpoint):
    def __init__(self, client: AsyncHTTPClient):
        super().__init__(client)
        self.base = BaseBilibiliEndpoint(client)
        self.base.type_checking = False

    @process_keyerror
    async def playurl(
        self,
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

    @process_keyerror
    async def comments(
        self,
        *,
        aid: Optional[int] = None,
        season_id: Optional[int] = None,
        index: Optional[int] = None,
        sort: CommentSortType = CommentSortType.TIME,
        page: int = 1,
        pagesize: int = 20
    ):  # NOTE: not same with origin
        if season_id is not None:
            assert index is not None, "parameter 'index' is required"
            season_info = await self.base.season_info(season_id=season_id)
            oid = season_info["result"]["episodes"][index - 1]["av_id"]
        elif aid is not None:
            oid = aid
        else:
            raise ClientSideException
        return await self.base.comments(
            oid=oid,
            sort=sort,
            type=CommentType.VIDEO,
            page=page,
            pagesize=pagesize,
        )

    async def search(
        self,
        *,
        keyword: str = "",
        type: SearchType = SearchType.search,
        page: int = 1,
        pagesize: int = 20,
        limit: int = 50
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

    async def rank(
        self,
        *,
        content: Union[RankContentType, RankBangumiType] = RankContentType.FULL_SITE,
        duration: RankDurationType = RankDurationType.THREE_DAY,
        new: bool = True
    ):
        if isinstance(content, int):
            return await self.base.rank_list(
                content=content,
                duration=duration,
                new=new,
            )
        else:
            return await self.base.rank_list_bangumi(
                site=content,
                duration=duration,
            )

    async def typedynamic(self):
        return await self.base.type_dynamic()

    async def recommend(self):
        return await self.base.recommend()

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

    async def archive(self, vmid: int, page: int = 1, pagesize: int = 10):
        return await self.base.space_archive(
            vmid=vmid,
            page=page,
            pagesize=pagesize,
        )

    async def favlist(self, fid: int, vmid: int, page: int = 1, pagesize: int = 20):
        return await self.base.favorite_video(
            fid=fid,
            vmid=vmid,
            page=page,
            pagesize=pagesize,
        )
