from typing import Callable, Coroutine

from fastapi import Depends, Request

from hibiapi.api.wallpaper import (
    Config,
    EndpointsType,
    NetRequest,
    OrderType,
    WallpaperCategoryType,
    WallpaperEndpoint,
)
from hibiapi.utils.routing import SlashRouter, exclude_params

__mount__, __config__ = "wallpaper", Config
router = SlashRouter(tags=["Wallpaper"])

WallpaperAPIRoot = NetRequest()


async def request_client():
    async with WallpaperAPIRoot as client:
        yield WallpaperEndpoint(client)


@router.get("/", summary="爱壁纸 API 兼容实现", deprecated=True)
async def _match_all(
    request: Request,
    type: EndpointsType = EndpointsType.wallpaper,
    endpoint: WallpaperEndpoint = Depends(request_client),
):
    func: Callable[..., Coroutine] = getattr(endpoint, type)
    return await func(**exclude_params(func, request.query_params))


@router.get(EndpointsType.wallpaper)
async def wallpaper(
    category: WallpaperCategoryType,
    limit: int = 20,
    skip: int = 0,
    adult: bool = True,
    order: OrderType = OrderType.hot,
    endpoint: WallpaperEndpoint = Depends(request_client),
):
    """
    ## Name: `wallpaper`

    > 横版壁纸

    ---

    ### Required:

    - ***WallpaperCategoryType*** **`category` = `WallpaperCategoryType.girl`**
        - Description: 分类

    ---

    ### Optional:
    - ***int*** `limit` = `20`
        - Description: 指定返回结果数量, 范围[20, 49]

    - ***int*** `skip` = `0`
        - Description: 跳过的壁纸数

    - ***bool*** `adult` = `true`
        - Description: NSFW开关, 没太大效果

    - ***OrderType*** `order` = `OrderType.hot`
        - Description: 搜索结果排序

    """

    return await endpoint.wallpaper(
        category=category, limit=limit, skip=skip, adult=adult, order=order
    )


@router.get(EndpointsType.vertical)
async def vertical(
    category: WallpaperCategoryType,
    limit: int = 20,
    skip: int = 0,
    adult: bool = True,
    order: OrderType = OrderType.hot,
    endpoint: WallpaperEndpoint = Depends(request_client),
):
    """
    ## Name: `vertical`

    > 竖版壁纸

    ---

    ### Required:

    - ***WallpaperCategoryType*** **`category` = `WallpaperCategoryType.girl`**
        - Description: 分类

    ---

    ### Optional:
    - ***int*** `limit` = `20`
        - Description: 指定返回结果数量, 范围[20, 49]

    - ***int*** `skip` = `0`
        - Description: 跳过的壁纸数

    - ***bool*** `adult` = `true`
        - Description: NSFW开关, 没太大效果

    - ***OrderType*** `order` = `OrderType.hot`
        - Description: 搜索结果排序

    """

    return await endpoint.vertical(
        category=category, limit=limit, skip=skip, adult=adult, order=order
    )
