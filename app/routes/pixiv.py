import asyncio
from typing import Callable, Coroutine, NoReturn, Optional

from api.pixiv import (
    EndpointsType,
    IllustType,
    PixivAPI,
    PixivConstants,
    PixivEndpoints,
    RankingDate,
    RankingType,
    SearchDurationType,
    SearchModeType,
    SearchSortType,
)
from fastapi import Depends, Request
from utils.log import logger
from utils.utils import SlashRouter, exclude_params

router = SlashRouter(tags=["Pixiv"])


PixivAPIRoot = PixivAPI()


async def requestClient():
    async with PixivAPIRoot.net as client:
        yield PixivEndpoints(client)


@router.on_event("startup")
async def login():
    async def _refreshIdentity() -> NoReturn:
        while True:
            logger.info("Start trying to login pixiv account")
            try:
                await PixivAPIRoot.login()
            except Exception:
                logger.exception("Exception occurred during trying to login account:")
            await asyncio.sleep(
                PixivConstants.CONFIG["account"]["refresh-interval"].as_number()
            )

    await PixivAPIRoot.login()
    asyncio.ensure_future(_refreshIdentity())


@router.get("/", summary="Pixiv API 兼容实现")
async def matchAll(
    request: Request,
    type: EndpointsType = EndpointsType.illust,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    func: Callable[..., Coroutine] = getattr(endpoint, type)
    return await func(**exclude_params(func, request.query_params))


@router.get(EndpointsType.illust)
async def illust(id: int, endpoint: PixivEndpoints = Depends(requestClient)):
    """
    ## Name: `illust`

    > 通过插画ID获取插画信息

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 插画ID

    """
    return await endpoint.illust(id=id)


@router.get(EndpointsType.member)
async def member(id: int, endpoint: PixivEndpoints = Depends(requestClient)):
    """
    ## Name: `member`

    > 通过用户ID获取用户信息

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 用户ID

    """
    return await endpoint.member(id=id)


@router.get(EndpointsType.member_illust)
async def member_illust(
    id: int,
    illust_type: IllustType = IllustType.illust,
    page: int = 1,
    size: int = 20,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    """
    ## Name: `member_illust`

    > 通过用户ID获取用户作品列表

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 用户ID

    ---

    ### Optional:
    - ***IllustType*** `illust_type` = `IllustType.illust`
        - Description: 作品类型
    - ***int*** `page` = `1`
        - Description: 页数
    - ***int*** `size` = `20`
        - Description: 包含作品大小

    """
    return await endpoint.member_illust(
        id=id, illust_type=illust_type, page=page, size=size
    )


@router.get(EndpointsType.favorite)
async def favorite(
    id: int,
    tag: Optional[str] = None,
    max_bookmark_id: Optional[int] = None,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    """
    ## Name: `favorite`

    > 查看用户收藏

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 用户ID

    ---

    ### Optional:
    - ***Optional[str]*** `tag` = `None`
        - Description: 包含的标签
    - ***Optional[int]*** `max_bookmark_id` = `None`
        - Description: 意义不明

    """
    return await endpoint.favorite(id=id, tag=tag, max_bookmark_id=max_bookmark_id)


@router.get(EndpointsType.following)
async def following(
    id: int,
    page: int = 1,
    size: int = 20,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    """
    ## Name: `following`

    > 获取用户关注列表

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 用户ID

    ---

    ### Optional:
    - ***int*** `page` = `1`
        - Description: 页数
    - ***int*** `size` = `20`
        - Description: 页面包含用户数目

    """
    return await endpoint.following(id=id, page=page, size=size)


@router.get(EndpointsType.follower)
async def follower(
    id: int,
    page: int = 1,
    size: int = 20,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    """
    ## Name: `following`

    > 获取用户粉丝列表

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 用户ID

    ---

    ### Optional:
    - ***int*** `page` = `1`
        - Description: 页数
    - ***int*** `size` = `20`
        - Description: 页面包含用户数目

    """
    return await endpoint.follower(id=id, page=page, size=size)


@router.get(EndpointsType.rank)
async def rank(
    mode: RankingType = RankingType.week,
    date: Optional[RankingDate] = None,
    page: int = 1,
    size: int = 50,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    """
    ## Name: `rank`

    > 获取作品排行榜

    ---

    ### Optional:
    - ***RankingType*** `mode` = `RankingType.week`
        - Description: 排行榜类型
    - ***Optional[RankingDate]*** `date` = `None`
        - Description: 日期, 格式 `yyyy-mm-dd`
    - ***int*** `page` = `1`
        - Description: 页数
    - ***int*** `size` = `50`
        - Description: 页面包含作品数

    """
    return await endpoint.rank(mode=mode, date=date, page=page, size=size)


@router.get(EndpointsType.search)
async def search(
    word: str,
    mode: SearchModeType = SearchModeType.partial_match_for_tags,
    order: SearchSortType = SearchSortType.date_desc,
    duration: Optional[SearchDurationType] = None,
    page: int = 1,
    size: int = 50,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    """
    ## Name: `search`

    > 通过关键词搜索作品

    ---

    ### Required:

    - ***str*** **`word`**
        - Description: 作品关键词

    ---

    ### Optional:
    - ***SearchModeType*** `mode` = `SearchModeType.partial_match_for_tags`
        - Description: 搜索匹配方法
    - ***SearchSortType*** `order` = `SearchSortType.date_desc`
        - Description: 搜索排序方法
    - ***Optional[SearchDurationType]*** `duration` = `None`
        - Description: 搜索作品时段
    - ***int*** `page` = `1`
        - Description: 页数
    - ***int*** `size` = `50`
        - Description: 页面包含作品数

    """
    return await endpoint.search(
        word=word, mode=mode, order=order, duration=duration, page=page, size=size
    )


@router.get(EndpointsType.tags)
async def tags(endpoint: PixivEndpoints = Depends(requestClient)):
    """
    ## Name: `tags`

    > 获取热门搜索标签

    """
    return await endpoint.tags()


@router.get(EndpointsType.related)
async def related(
    id: int,
    page: int = 1,
    size: int = 20,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    """
    ## Name: `related`

    > 获取相关画作推荐

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 原插画ID

    ---

    ### Optional:
    - ***int*** `page` = `1`
        - Description: 页数
    - ***int*** `size` = `20`
        - Description: 页面包含作品数

    """
    return await endpoint.related(id=id, page=page, size=size)


@router.get(EndpointsType.ugoira_metadata)
async def ugoira_metadata(id: int, endpoint: PixivEndpoints = Depends(requestClient)):
    """
    ## Name: `ugoira_metadata`

    > 获取动图信息

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 该动图的作品ID

    """
    return await endpoint.ugoira_metadata(id=id)
