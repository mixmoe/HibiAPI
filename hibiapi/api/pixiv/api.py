from datetime import date, timedelta
from enum import Enum
from typing import Any, Dict, Optional, cast

from hibiapi.api.pixiv.constants import PixivConstants
from hibiapi.api.pixiv.net import NetRequest as PixivNetClient
from hibiapi.utils.cache import cache_config
from hibiapi.utils.decorators import enum_auto_doc
from hibiapi.utils.net import catch_network_error
from hibiapi.utils.routing import BaseEndpoint, dont_route, request_headers


@enum_auto_doc
class IllustType(str, Enum):
    """画作类型"""

    illust = "illust"
    """插画"""
    manga = "manga"
    """漫画"""


@enum_auto_doc
class RankingType(str, Enum):
    """排行榜内容类型"""

    day = "day"
    """日榜"""
    week = "week"
    """周榜"""
    month = "month"
    """月榜"""
    day_male = "day_male"
    """男性向"""
    day_female = "day_female"
    """女性向"""
    week_original = "week_original"
    """原创周榜"""
    week_rookie = "week_rookie"
    """新人周榜"""
    day_ai = "day_ai"
    """AI日榜"""
    day_r18 = "day_r18"
    day_male_r18 = "day_male_r18"
    day_female_r18 = "day_female_r18"
    week_r18 = "week_r18"
    week_r18g = "week_r18g"
    day_r18_ai = "day_r18_ai"


@enum_auto_doc
class SearchModeType(str, Enum):
    """搜索匹配类型"""

    partial_match_for_tags = "partial_match_for_tags"
    """标签部分一致"""
    exact_match_for_tags = "exact_match_for_tags"
    """标签完全一致"""
    title_and_caption = "title_and_caption"
    """标题说明文"""


@enum_auto_doc
class SearchNovelModeType(str, Enum):
    """搜索匹配类型"""

    partial_match_for_tags = "partial_match_for_tags"
    """标签部分一致"""
    exact_match_for_tags = "exact_match_for_tags"
    """标签完全一致"""
    text = "text"
    """正文"""
    keywords = "keywords"
    """关键词"""


@enum_auto_doc
class SearchSortType(str, Enum):
    """搜索排序类型"""

    date_desc = "date_desc"
    """按日期倒序"""
    date_asc = "date_asc"
    """按日期正序"""
    popular_desc = "popular_desc"
    """受欢迎降序(Premium功能)"""


@enum_auto_doc
class SearchDurationType(str, Enum):
    """搜索时段类型"""

    within_last_day = "within_last_day"
    """一天内"""
    within_last_week = "within_last_week"
    """一周内"""
    within_last_month = "within_last_month"
    """一个月内"""


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


class PixivEndpoints(BaseEndpoint):
    @staticmethod
    def _parse_accept_language(accept_language: str) -> str:
        first_language, *_ = accept_language.partition(",")
        language_code, *_ = first_language.partition(";")
        return language_code.lower().strip()

    @dont_route
    @catch_network_error
    async def request(
        self, endpoint: str, *, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        headers = self.client.headers.copy()
        net_client = cast(PixivNetClient, self.client.net_client)
        auth, token = net_client.get_available_user()
        if auth is None:
            auth = await net_client.auth(token)
        headers["Authorization"] = f"Bearer {auth.access_token}"

        if language := request_headers.get().get("Accept-Language"):
            language = self._parse_accept_language(language)
            headers["Accept-Language"] = language
        response = await self.client.get(
            self._join(
                base=PixivConstants.APP_HOST,
                endpoint=endpoint,
                params=params or {},
            ),
            headers=headers,
        )
        return response.json()

    @cache_config(ttl=timedelta(days=3))
    async def illust(self, *, id: int):
        return await self.request("v1/illust/detail", params={"illust_id": id})

    @cache_config(ttl=timedelta(days=1))
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

    @cache_config(ttl=timedelta(hours=12))
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

    @cache_config(ttl=timedelta(hours=12))
    async def tags(self):
        return await self.request("v1/trending-tags/illust")

    @cache_config(ttl=timedelta(minutes=15))
    async def related(self, *, id: int, page: int = 1, size: int = 20):
        return await self.request(
            "v2/illust/related",
            params={
                "illust_id": id,
                "offset": (page - 1) * size,
            },
        )

    @cache_config(ttl=timedelta(days=3))
    async def ugoira_metadata(self, *, id: int):
        return await self.request(
            "v1/ugoira/metadata",
            params={
                "illust_id": id,
            },
        )

    async def member_novel(self, *, id: int, page: int = 1, size: int = 20):
        return await self.request(
            "/v1/user/novels",
            params={
                "user_id": id,
                "offset": (page - 1) * size,
            },
        )

    async def novel_series(self, *, id: int):
        return await self.request("/v2/novel/series", params={"series_id": id})

    async def novel_detail(self, *, id: int):
        return await self.request("/v2/novel/detail", params={"novel_id": id})

    async def novel_text(self, *, id: int):
        return await self.request("/v1/novel/text", params={"novel_id": id})

    async def search_novel(
        self,
        *,
        word: str,
        mode: SearchNovelModeType = SearchNovelModeType.partial_match_for_tags,
        sort: SearchSortType = SearchSortType.date_desc,
        merge_plain_keyword_results: bool = True,
        include_translated_tag_results: bool = True,
        duration: Optional[SearchDurationType] = None,
        page: int = 1,
        size: int = 50,
    ):
        return await self.request(
            "/v1/search/novel",
            params={
                "word": word,
                "search_target": mode,
                "sort": sort,
                "merge_plain_keyword_results": merge_plain_keyword_results,
                "include_translated_tag_results": include_translated_tag_results,
                "duration": duration,
                "offset": (page - 1) * size,
            },
        )

    async def novel_new(self, *, max_novel_id: Optional[int] = None):
        return await self.request(
            "/v1/novel/new", params={"max_novel_id": max_novel_id}
        )
