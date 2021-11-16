from datetime import timedelta
from enum import Enum
from typing import Any, Dict, Optional

from hibiapi.utils.cache import cache_config, disable_cache
from hibiapi.utils.config import APIConfig
from hibiapi.utils.net import catch_network_error
from hibiapi.utils.routing import BaseEndpoint

Config = APIConfig("wallpaper")


class EndpointsType(str, Enum):
    wallpaper = "wallpaper"
    vertical = "vertical"


class Category(str, Enum):
    """
    壁纸分类

    | **数值** | **含义** |
    |---|---|
    | girl | 女生 |
    | animal | 动物 |
    | landscape | 自然 |
    | anime | 二次元 |
    | drawn | 手绘 |
    | mechanics | 机械 |
    | boy | 男生 |
    | game | 游戏 |
    | text | 文字 |
    """

    girl = "girl"
    animal = "animal"
    landscape = "landscape"
    anime = "anime"
    drawn = "drawn"
    mechanics = "mechanics"
    boy = "boy"
    game = "game"
    text = "text"


CATEGORY: Dict[Category, str] = {
    Category.girl: "4e4d610cdf714d2966000000",
    Category.animal: "4e4d610cdf714d2966000001",
    Category.landscape: "4e4d610cdf714d2966000002",
    Category.anime: "4e4d610cdf714d2966000003",
    Category.drawn: "4e4d610cdf714d2966000004",
    Category.mechanics: "4e4d610cdf714d2966000005",
    Category.boy: "4e4d610cdf714d2966000006",
    Category.game: "4e4d610cdf714d2966000007",
    Category.text: "5109e04e48d5b9364ae9ac45",
}


class OrderType(str, Enum):
    hot = "hot"
    new = "new"


class WallpaperEndpoint(BaseEndpoint):
    base = "http://service.aibizhi.adesk.com"

    @disable_cache
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
        category: Category,
        limit: int = 20,
        skip: int = 0,
        adult: bool = True,
        order: OrderType = OrderType.hot,
    ):

        return await self.request(
            f"v1/wallpaper/category/{CATEGORY[category]}/wallpaper",
            params={
                "limit": limit,
                "skip": skip,
                "adult": adult,
                "order": order,
                "first": 0,
            },
        )

    # 壁纸有防盗链token, 不建议长时间缓存
    @cache_config(ttl=timedelta(hours=2))
    async def vertical(
        self,
        *,
        category: Category,
        limit: int = 20,
        skip: int = 0,
        adult: bool = True,
        order: OrderType = OrderType.hot,
    ):

        return await self.request(
            f"v1/vertical/category/{CATEGORY[category]}/vertical",
            params={
                "limit": limit,
                "skip": skip,
                "adult": adult,
                "order": order,
                "first": 0,
            },
        )
