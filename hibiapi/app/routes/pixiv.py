import asyncio
from typing import Callable, Coroutine, NoReturn, Optional

from fastapi import Depends, Request

from hibiapi.api.pixiv import (
    EndpointsType,
    IllustType,
    PixivAPI,
    PixivConstants,
    PixivEndpoints,
    RankingDate,
    RankingType,
    SearchDurationType,
    SearchModeType,
    SearchNovelModeType,
    SearchSortType,
)
from hibiapi.utils.log import logger
from hibiapi.utils.routing import SlashRouter, exclude_params

if not PixivConstants.CONFIG["account"]["token"].get():
    logger.warning("Pixiv API token is not set, pixiv endpoint will be unavailable.")
    PixivConstants.CONFIG["enabled"].set(False)

__mount__, __config__ = "pixiv", PixivConstants.CONFIG
router = SlashRouter(tags=["Pixiv"])

PixivAPIRoot = PixivAPI()


async def request_client():
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
async def _match_all(
    request: Request,
    type: EndpointsType = EndpointsType.illust,
    endpoint: PixivEndpoints = Depends(request_client),
):
    func: Callable[..., Coroutine] = getattr(endpoint, type)
    return await func(**exclude_params(func, request.query_params))


@router.get(EndpointsType.illust)
async def illust(id: int, endpoint: PixivEndpoints = Depends(request_client)):
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
async def member(id: int, endpoint: PixivEndpoints = Depends(request_client)):
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
    endpoint: PixivEndpoints = Depends(request_client),
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
    endpoint: PixivEndpoints = Depends(request_client),
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
    endpoint: PixivEndpoints = Depends(request_client),
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
    endpoint: PixivEndpoints = Depends(request_client),
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
    endpoint: PixivEndpoints = Depends(request_client),
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
    endpoint: PixivEndpoints = Depends(request_client),
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
async def tags(endpoint: PixivEndpoints = Depends(request_client)):
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
    endpoint: PixivEndpoints = Depends(request_client),
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
async def ugoira_metadata(id: int, endpoint: PixivEndpoints = Depends(request_client)):
    """
    ## Name: `ugoira_metadata`

    > 获取动图信息

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 该动图的作品ID

    """
    return await endpoint.ugoira_metadata(id=id)


@router.get(EndpointsType.member_novel)
async def member_novel(
    id: int,
    page: int = 1,
    size: int = 20,
    endpoint: PixivEndpoints = Depends(request_client),
):
    """
    ## Name: `member_novel`

    > 通过用户ID获取用户小说列表

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 用户ID

    ---

    ### Optional:
    - ***int*** `page` = `1`
        - Description: 页数
    - ***int*** `size` = `20`
        - Description: 每页大小
    """

    return await endpoint.member_novels(id=id, page=page, size=size)


@router.get(EndpointsType.novel_series)
async def novel_series(id: int, endpoint: PixivEndpoints = Depends(request_client)):
    """
    ## Name: `novel_series`

    > 获取小说系列的信息

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 小说系列ID
    """
    return await endpoint.novel_series(id=id)


@router.get(EndpointsType.novel_detail)
async def novel_detail(id: int, endpoint: PixivEndpoints = Depends(request_client)):
    """
    ## Name: `novel_detail`

    > 获取小说信息

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 小说ID
    """
    return await endpoint.novel_detail(id=id)


@router.get(EndpointsType.novel_text)
async def novel_text(id: int, endpoint: PixivEndpoints = Depends(request_client)):
    """
    ## Name: `novel_text`

    > 获取小说正文

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 小说ID
    """
    return await endpoint.novel_text(id=id)


@router.get(EndpointsType.search_novel)
async def search_novel(
    word: str,
    mode: SearchNovelModeType = SearchNovelModeType.partial_match_for_tags,
    sort: SearchSortType = SearchSortType.date_desc,
    merge_plain_keyword_results: bool = True,
    include_translated_tag_results: bool = True,
    duration: Optional[SearchDurationType] = None,
    page: int = 1,
    size: int = 50,
    endpoint: PixivEndpoints = Depends(request_client),
):
    """
    ## Name: `search_novel`

    > 搜索小说

    ---

    ### Required:

    - ***str*** **`word`**
        - Description: 关键词

    ---

    ### Optional:
    - ***SearchNovelModeType*** `mode` = `SearchNovelModeType.partial_match_for_tags`
        - Description: 搜索匹配方法
    - ***SearchSortType*** `sort` = `SearchSortType.date_desc`
        - Description: 结果排序方式
    - ***bool*** `merge_plain_keyword_results` = `True`
        - Description: 是否包含合并提供的关键字的搜索结果
    - ***bool*** `include_translated_tag_results` = `True`
        - Description: 是否包含其他语言标签的搜索结果
    - ***Optional[SearchDurationType]*** `duration` = `None`
        - Description: 小说发表的时间段
    - ***int*** `page` = `1`
        - Description: 页数
    - ***int*** `size` = `50`
        - Description: 每页大小
    """
    return await endpoint.search_novel(
        word=word,
        mode=mode,
        sort=sort,
        merge_plain_keyword_results=merge_plain_keyword_results,
        include_translated_tag_results=include_translated_tag_results,
        duration=duration,
        page=page,
        size=size,
    )
