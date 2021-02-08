import json
from datetime import date, timedelta
from enum import Enum
from typing import Any, Dict, Optional

from utils.config import DATA_PATH
from utils.net import catch_network_error
from utils.routing import BaseEndpoint

from .constants import PixivConstants
from .net import NetRequest, UserInfo

USER_TEMP_DATA = DATA_PATH / "pixiv_account.json"


class EndpointsType(str, Enum):
    illust = "illust"
    member = "member"
    member_illust = "member_illust"
    favorite = "favorite"
    following = "following"
    follower = "follower"
    rank = "rank"
    search = "search"
    tags = "tags"
    related = "related"
    ugoira_metadata = "ugoira_metadata"


class IllustType(str, Enum):
    """
    画作类型

    | **数值** | **含义** |
    |---|---|
    | illust | 插画 |
    | manga | 漫画 |
    """

    illust = "illust"
    manga = "manga"


class RankingType(str, Enum):
    """
    排行榜内容类型

    | **数值** | **含义** |
    |---|---|
    | day  | 日榜 |
    | week  | 周榜 |
    | month  | 月榜 |
    | week_rookie  | 新人 |
    | week_original  | 原创 |
    | day_male  | 男性向 |
    | day_female  | 女性向 |
    | ...  | and more |
    """

    day = "day"
    week = "week"
    month = "month"
    day_male = "day_male"
    day_female = "day_female"
    week_original = "week_original"
    week_rookie = "week_rookie"
    day_r18 = "day_r18"
    day_male_r18 = "day_male_r18"
    day_female_r18 = "day_female_r18"
    week_r18 = "week_r18"
    week_r18g = "week_r18g"


class SearchModeType(str, Enum):
    """
    搜索匹配类型

    | **数值** | **含义** |
    |---|---|
    | partial_match_for_tags  | 标签部分一致 |
    | exact_match_for_tags  | 标签完全一致 |
    | title_and_caption  | 标题说明文 |
    """

    partial_match_for_tags = "partial_match_for_tags"
    exact_match_for_tags = "exact_match_for_tags"
    title_and_caption = "title_and_caption"


class SearchSortType(str, Enum):
    """
    搜索排序类型

    | **数值** | **含义** |
    |---|---|
    | date_desc  | 按日期倒序 |
    | date_asc  | 按日期正序 |
    """

    date_desc = "date_desc"
    date_asc = "date_asc"


class SearchDurationType(str, Enum):
    """
    搜索时段类型

    | **数值** | **含义** |
    |---|---|
    | within_last_day | 一天内 |
    | within_last_week | 一周内 |
    | within_last_month | 一个月内 |
    """

    within_last_day = "within_last_day"
    within_last_week = "within_last_week"
    within_last_month = "within_last_month"


class RankingDate(date):
    @classmethod
    def yesterday(cls) -> "RankingDate":
        yesterday = cls.today() - timedelta(days=1)
        return cls(yesterday.year, yesterday.month, yesterday.day)

    def toString(self) -> str:
        return self.strftime(r"%Y-%m-%d")

    @classmethod
    def new(cls, date: date) -> "RankingDate":
        return cls(date.year, date.month, date.day)


class PixivAPI:
    def __init__(self):
        pass

    async def login(self):
        if USER_TEMP_DATA.exists():
            user = await UserInfo.parse_obj(
                json.loads(USER_TEMP_DATA.read_text(encoding="utf-8"))
            ).renew()
        else:
            user = await UserInfo.login(
                account=(
                    PixivConstants.CONFIG["account"]["username"].as_str(),
                    PixivConstants.CONFIG["account"]["password"].as_str(),
                )
            )
        self.user = user
        self.net = NetRequest(user)
        USER_TEMP_DATA.write_text(
            user.json(sort_keys=True, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )


class PixivEndpoints(BaseEndpoint):
    @catch_network_error
    async def request(
        self, endpoint: str, *, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        response = await self.client.get(
            self._join(
                base=PixivConstants.APP_HOST,
                endpoint=endpoint,
                params=params or {},
            )
        )
        return response.json()

    async def illust(self, *, id: int):
        return await self.request("v1/illust/detail", params={"illust_id": id})

    async def member(self, *, id: int):
        return await self.request("v1/user/detail", params={"user_id": id})

    async def member_illust(
        self,
        *,
        id: int,
        illust_type: IllustType = IllustType.illust,
        page: int = 1,
        size: int = 20,
    ):
        return await self.request(
            "v1/user/illusts",
            params={
                "user_id": id,
                "type": illust_type,
                "offset": (page - 1) * size,
            },
        )

    async def favorite(
        self,
        *,
        id: int,
        tag: Optional[str] = None,
        max_bookmark_id: Optional[int] = None,
    ):
        return await self.request(
            "v1/user/bookmarks/illust",
            params={
                "user_id": id,
                "tag": tag,
                "restrict": "public",
                "max_bookmark_id": max_bookmark_id or None,
            },
        )

    async def following(self, *, id: int, page: int = 1, size: int = 20):
        return await self.request(
            "v1/user/following",
            params={
                "user_id": id,
                "offset": (page - 1) * size,
            },
        )

    async def follower(self, *, id: int, page: int = 1, size: int = 20):
        return await self.request(
            "v1/user/follower",
            params={
                "user_id": id,
                "offset": (page - 1) * size,
            },
        )

    async def rank(
        self,
        *,
        mode: RankingType = RankingType.week,
        date: Optional[RankingDate] = None,
        page: int = 1,
        size: int = 50,
    ):
        return await self.request(
            "v1/illust/ranking",
            params={
                "mode": mode,
                "date": RankingDate.new(date or RankingDate.yesterday()).toString(),
                "offset": (page - 1) * size,
            },
        )

    async def search(
        self,
        *,
        word: str,
        mode: SearchModeType = SearchModeType.partial_match_for_tags,
        order: SearchSortType = SearchSortType.date_desc,
        duration: Optional[SearchDurationType] = None,
        page: int = 1,
        size: int = 50,
    ):
        return await self.request(
            "v1/search/illust",
            params={
                "word": word,
                "search_target": mode,
                "sort": order,
                "duration": duration,
                "offset": (page - 1) * size,
            },
        )

    async def tags(self):
        return await self.request("v1/trending-tags/illust")

    async def related(self, id: int, page: int = 1, size: int = 20):
        return await self.request(
            "v2/illust/related",
            params={
                "illust_id": id,
                "offset": (page - 1) * size,
            },
        )

    async def ugoira_metadata(self, *, id: int):
        return await self.request(
            "v1/ugoira/metadata",
            params={
                "illust_id": id,
            },
        )
