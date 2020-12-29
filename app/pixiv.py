import asyncio
import inspect
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
from utils.utils import SlashRouter

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
                PixivConstants.CONFIG["account"]["refresh_interval"].as_number()
            )

    asyncio.ensure_future(_refreshIdentity())


@router.get("/", summary="Pixiv API 兼容实现")
async def matchAll(
    request: Request,
    type: EndpointsType = EndpointsType.illust,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    func: Callable[..., Coroutine] = getattr(endpoint, type)
    params = inspect.signature(func).parameters
    return await func(**{k: v for k, v in request.query_params.items() if k in params})


@router.get(EndpointsType.illust)
async def illust(id: int, endpoint: PixivEndpoints = Depends(requestClient)):
    return await endpoint.illust(id=id)


@router.get(EndpointsType.member)
async def member(id: int, endpoint: PixivEndpoints = Depends(requestClient)):
    return await endpoint.member(id=id)


@router.get(EndpointsType.member_illust)
async def member_illust(
    id: int,
    illust_type: IllustType = IllustType.illust,
    page: int = 1,
    size: int = 20,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    return await endpoint.member_illust(
        id=id, illust_type=illust_type, page=page, size=size
    )


@router.get(EndpointsType.favorite)
async def favorite(
    id: int,
    tag: Optional[str] = None,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    return await endpoint.favorite(id=id, tag=tag)


@router.get(EndpointsType.following)
async def following(
    id: int,
    page: int = 1,
    size: int = 20,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    return await endpoint.following(id=id, page=page, size=size)


@router.get(EndpointsType.follower)
async def follower(
    id: int,
    page: int = 1,
    size: int = 20,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    return await endpoint.follower(id=id, page=page, size=size)


@router.get(EndpointsType.rank)
async def rank(
    mode: RankingType = RankingType.week,
    date: Optional[RankingDate] = None,
    page: int = 1,
    size: int = 50,
    endpoint: PixivEndpoints = Depends(requestClient),
):
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
    return await endpoint.search(
        word=word, mode=mode, order=order, duration=duration, page=page, size=size
    )


@router.get(EndpointsType.tags)
async def tags(endpoint: PixivEndpoints = Depends(requestClient)):
    return await endpoint.tags()


@router.get(EndpointsType.related)
async def related(
    id: int,
    page: int = 1,
    size: int = 20,
    endpoint: PixivEndpoints = Depends(requestClient),
):
    return await endpoint.related(id=id, page=page, size=size)


@router.get(EndpointsType.ugoira_metadata)
async def ugoira_metadata(id: int, endpoint: PixivEndpoints = Depends(requestClient)):
    return await endpoint.ugoira_metadata(id=id)
