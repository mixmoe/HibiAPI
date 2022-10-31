from typing import Callable, Coroutine

from fastapi import Depends, Header, Request

from hibiapi.api.bika import (
    BikaConstants,
    BikaEndpoints,
    BikaLogin,
    EndpointsType,
    ImageQuality,
    NetRequest,
    ResultSort,
)
from hibiapi.utils.log import logger
from hibiapi.utils.routing import SlashRouter, exclude_params

try:
    BikaConstants.CONFIG["account"].get(BikaLogin)
except Exception as e:
    logger.warning(f"Bika account misconfigured: {e}")
    BikaConstants.CONFIG["enabled"].set(False)


async def x_image_quality(x_image_quality: ImageQuality = Header(ImageQuality.medium)):
    if x_image_quality is None:
        return BikaConstants.CONFIG["image_quality"].get(ImageQuality)
    return x_image_quality


__mount__, __config__ = "bika", BikaConstants.CONFIG
router = SlashRouter(tags=["Bika"], dependencies=[Depends(x_image_quality)])

BikaAPIRoot = NetRequest()


async def request_client():
    async with BikaAPIRoot as client:
        yield BikaEndpoints(client)


@router.get("/", summary="Bika API Root", deprecated=True)
async def _match_all(
    request: Request,
    type: EndpointsType,
    endpoint: BikaEndpoints = Depends(request_client),
):
    func: Callable[..., Coroutine] = getattr(endpoint, type)
    return await func(**exclude_params(func, request.query_params))


@router.get(EndpointsType.collections)
async def collections(endpoint: BikaEndpoints = Depends(request_client)):
    return await endpoint.collections()


@router.get(EndpointsType.categories)
async def categories(endpoint: BikaEndpoints = Depends(request_client)):
    return await endpoint.categories()


@router.get(EndpointsType.keywords)
async def keywords(endpoint: BikaEndpoints = Depends(request_client)):
    return await endpoint.keywords()


@router.get(EndpointsType.advanced_search)
async def advanced_search(
    keyword: str,
    page: int = 1,
    sort: ResultSort = ResultSort.date_descending,
    endpoint: BikaEndpoints = Depends(request_client),
):
    return await endpoint.advanced_search(
        keyword=keyword,
        page=page,
        sort=sort,
    )


@router.get(EndpointsType.category_list)
async def category_list(
    category: str,
    page: int = 1,
    sort: ResultSort = ResultSort.date_descending,
    endpoint: BikaEndpoints = Depends(request_client),
):
    return await endpoint.category_list(
        category=category,
        page=page,
        sort=sort,
    )


@router.get(EndpointsType.author_list)
async def author_list(
    author: str,
    page: int = 1,
    sort: ResultSort = ResultSort.date_descending,
    endpoint: BikaEndpoints = Depends(request_client),
):
    return await endpoint.author_list(
        author=author,
        page=page,
        sort=sort,
    )


@router.get(EndpointsType.comic_detail)
async def comic_detail(id: str, endpoint: BikaEndpoints = Depends(request_client)):
    return await endpoint.comic_detail(id=id)


@router.get(EndpointsType.comic_recommendation)
async def comic_recommendation(
    id: str, endpoint: BikaEndpoints = Depends(request_client)
):
    return await endpoint.comic_recommendation(id=id)


@router.get(EndpointsType.comic_episodes)
async def comic_episodes(
    id: str, page: int = 1, endpoint: BikaEndpoints = Depends(request_client)
):
    return await endpoint.comic_episodes(id=id, page=page)


@router.get(EndpointsType.comic_page)
async def comic_page(
    id: str,
    order: int = 1,
    page: int = 1,
    endpoint: BikaEndpoints = Depends(request_client),
):
    return await endpoint.comic_page(id=id, order=order, page=page)


@router.get(EndpointsType.comic_comments)
async def comic_comments(
    id: str, page: int = 1, endpoint: BikaEndpoints = Depends(request_client)
):
    return await endpoint.comic_comments(id=id, page=page)


@router.get(EndpointsType.games)
async def games(page: int = 1, endpoint: BikaEndpoints = Depends(request_client)):
    return await endpoint.games(page=page)


@router.get(EndpointsType.game_detail)
async def game_detail(id: str, endpoint: BikaEndpoints = Depends(request_client)):
    return await endpoint.game_detail(id=id)
