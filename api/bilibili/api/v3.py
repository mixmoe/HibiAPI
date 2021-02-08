from enum import Enum

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


class V3EndpointsType(str, Enum):
    video_info = "video_info"
    video_address = "video_address"
    video_recommend = "video_recommend"
    video_dynamic = "video_dynamic"
    video_ranking = "video_ranking"

    user_info = "user_info"
    user_uploaded = "user_uploaded"
    user_favorite = "user_favorite"

    season_info = "season_info"
    season_recommend = "season_recommend"
    season_episode = "season_episode"
    season_ranking = "season_ranking"
    season_timeline = "season_timeline"

    search = "search"
    search_recommend = "search_recommend"
    search_suggestion = "search_suggestion"

    comments = "comments"


class BilibiliEndpointV3(BaseEndpoint):
    def __init__(self, client: AsyncHTTPClient):
        super().__init__(client)
        self.base = BaseBilibiliEndpoint(client)
        self.base.type_checking = False

    async def video_info(self, *, aid: int):
        return await self.base.view(aid=aid)

    async def video_address(
        self,
        *,
        aid: int,
        cid: int,
        quality: VideoQualityType = VideoQualityType.VIDEO_480P,
        type: VideoFormatType = VideoFormatType.FLV,
    ):
        return await self.base.playurl(
            aid=aid,
            cid=cid,
            quality=quality,
            type=type,
        )

    async def video_recommend(
        self,
    ):
        return await self.base.recommend()

    async def video_dynamic(self):
        return await self.base.type_dynamic()

    async def video_ranking(
        self,
        type: RankContentType = RankContentType.FULL_SITE,
        duration: RankDurationType = RankDurationType.THREE_DAY,
    ):
        return await self.base.rank_list(
            content=type,
            duration=duration,
        )

    async def user_info(self, *, uid: int, page: int = 1, size: int = 10):
        return await self.base.space(
            vmid=uid,
            page=page,
            pagesize=size,
        )

    async def user_uploaded(self, *, uid: int, page: int = 1, size: int = 10):
        return await self.base.space_archive(
            vmid=uid,
            page=page,
            pagesize=size,
        )

    async def user_favorite(self, *, uid: int, fid: int, page: int = 1, size: int = 10):
        return await self.base.favorite_video(
            fid=fid,
            vmid=uid,
            page=page,
            pagesize=size,
        )

    async def season_info(self, *, season_id: int):
        return await self.base.season_info(season_id=season_id)

    async def season_recommend(self, *, season_id: int):
        return await self.base.season_recommend(season_id=season_id)

    async def season_episode(self, episode_id: int):
        return await self.base.bangumi_source(episode_id=episode_id)

    async def season_timeline(self, type: TimelineType = TimelineType.GLOBAL):
        return await self.base.timeline(type=type)

    async def season_ranking(
        self,
        *,
        type: RankBangumiType = RankBangumiType.GLOBAL,
        duration: RankDurationType = RankDurationType.THREE_DAY,
    ):
        return await self.base.rank_list_bangumi(
            site=type,
            duration=duration,
        )

    async def search(self, keyword: str, page: int = 1, size: int = 20):
        return await self.base.search(
            keyword=keyword,
            page=page,
            pagesize=size,
        )

    async def search_recommend(self, *, limit: int = 50):
        return await self.base.search_hot(limit=limit)

    async def search_suggestion(self, *, keyword: str):
        return await self.base.search_suggest(keyword=keyword)

    async def comments(
        self,
        *,
        id: int,
        type: CommentType = CommentType.VIDEO,
        sort: CommentSortType = CommentSortType.TIME,
        page: int = 1,
        size: int = 20,
    ):
        return await self.base.comments(
            oid=id,
            type=type,
            sort=sort,
            page=page,
            pagesize=size,
        )
