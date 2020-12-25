from enum import Enum
from typing import Union

from utils.utils import AsyncHTTPClient, BaseEndpoint

from .base import BaseBilibiliEndpoint, TimelineType


class SearchType(str, Enum):
    search = "search"
    suggest = "suggest"
    hot = "hot"


class RankType(str, Enum):
    all = "all"
    origin = "origin"
    rookie = "rookie"
    bangumi = "bangumi"


class BilibiliEndpointV2(BaseEndpoint):
    def __init__(self, client: AsyncHTTPClient):
        super().__init__(client)
        self.base = BaseBilibiliEndpoint(client)
        self.base.type_checking = False

    async def playurl(self, aid: int):
        return self.base.view(aid=aid)

    async def seasoninfo(self, *, season_id: int):
        return await self.base.season_info_web(season_id=season_id)

    async def source(self, *, episode_id: int):
        return await self.base.bangumi_source(episode_id=episode_id)

    async def seasonrecommend(self, *, season_id: int):
        return await self.base.season_recommend(season_id=season_id)

    async def comments(self, *, aid: int, sort: int = 0):
        return await self.base.comments(aid=aid, sort=sort)

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
            return await self.base.search(keyword=keyword, page=page, pagesize=pagesize)

    async def rank(
        self,
        *,
        type: RankType = RankType.all,
        content: Union[str, int] = 0,
        duration: int = 3,
        new: bool = True
    ):
        if isinstance(content, int):
            return await self.base.rank_list(
                type=type, content=content, duration=duration, new=new
            )
        else:
            return self.base.rank_list_bangumi(site=content, duration=duration)

    async def typedynamic(self):
        return await self.base.type_dynamic()

    async def recommend(self):
        return await self.base.recommend()

    async def timeline(self, *, type: TimelineType = TimelineType.GLOBAL):
        return await self.base.timeline(type=type)

    async def space(self, *, vmid: int, page: int = 1, pagesize: int = 10):
        return await self.base.space(vmid=vmid, page=page, pagesize=pagesize)

    async def archive(self, vmid: int, page: int = 1, pagesize: int = 10):
        return await self.base.space_archive(vmid=vmid, page=page, pagesize=pagesize)

    async def favlist(self, fid: int, vmid: int, page: int = 1, pagesize: int = 20):
        return await self.base.favorite_video(
            fid=fid, vmid=vmid, page=page, pagesize=pagesize
        )
