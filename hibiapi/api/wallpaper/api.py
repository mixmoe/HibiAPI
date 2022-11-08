from datetime import timedelta
from enum import Enum
from typing import Any, Dict, Optional

from hibiapi.utils.cache import cache_config
from hibiapi.utils.config import APIConfig
from hibiapi.utils.decorators import enum_auto_doc
from hibiapi.utils.net import catch_network_error
from hibiapi.utils.routing import BaseEndpoint, dont_route

Config = APIConfig("wallpaper")


@enum_auto_doc
class WallpaperCategoryType(str, Enum):
    """壁纸分类"""

    girl = "girl"
    """女生"""
    animal = "animal"
    """动物"""
    landscape = "landscape"
    """自然"""
    anime = "anime"
    """二次元"""
    drawn = "drawn"
    """手绘"""
    mechanics = "mechanics"
    """机械"""
    boy = "boy"
    """男生"""
    game = "game"
    """游戏"""
    text = "text"
    """文字"""


CATEGORY: Dict[WallpaperCategoryType, str] = {
    WallpaperCategoryType.girl: "4e4d610cdf714d2966000000",
    WallpaperCategoryType.animal: "4e4d610cdf714d2966000001",
    WallpaperCategoryType.landscape: "4e4d610cdf714d2966000002",
    WallpaperCategoryType.anime: "4e4d610cdf714d2966000003",
    WallpaperCategoryType.drawn: "4e4d610cdf714d2966000004",
    WallpaperCategoryType.mechanics: "4e4d610cdf714d2966000005",
    WallpaperCategoryType.boy: "4e4d610cdf714d2966000006",
    WallpaperCategoryType.game: "4e4d610cdf714d2966000007",
    WallpaperCategoryType.text: "5109e04e48d5b9364ae9ac45",
}


@enum_auto_doc
class WallpaperOrderType(str, Enum):
    """壁纸排序方式"""

    hot = "hot"
    """热门"""
    new = "new"
    """最新"""


class WallpaperEndpoint(BaseEndpoint):
    base = "http://service.aibizhi.adesk.com"

    @dont_route
    @catch_network_error
    async def request(
        self, endpoint: str, *, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        response = await self.client.get(
            self._join(
                base=WallpaperEndpoint.base,
                endpoint=endpoint,
                params=params or {},
            )
        )
        return response.json()

    # 壁纸有防盗链token, 不建议长时间缓存
    @cache_config(ttl=timedelta(hours=2))
    async def wallpaper(
        self,
        *,
        category: WallpaperCategoryType,
        limit: int = 20,
        skip: int = 0,
        adult: bool = True,
        order: WallpaperOrderType = WallpaperOrderType.hot,
    ):

        return await self.request(
            "v1/wallpaper/category/{category}/wallpaper",
            params={
                "limit": limit,
                "skip": skip,
                "adult": adult,
                "order": order,
                "first": 0,
                "category": CATEGORY[category],
            },
        )

    # 壁纸有防盗链token, 不建议长时间缓存
    @cache_config(ttl=timedelta(hours=2))
    async def vertical(
        self,
        *,
        category: WallpaperCategoryType,
        limit: int = 20,
        skip: int = 0,
        adult: bool = True,
        order: WallpaperOrderType = WallpaperOrderType.hot,
    ):

        return await self.request(
            "v1/vertical/category/{category}/vertical",
            params={
                "limit": limit,
                "skip": skip,
                "adult": adult,
                "order": order,
                "first": 0,
                "category": CATEGORY[category],
            },
        )
