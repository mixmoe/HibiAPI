from typing import Callable, Coroutine, Optional, Union

from api.bilibili import (
    BilibiliEndpointV2,
    CommentSortType,
    NetRequest,
    RankBangumiType,
    RankContentType,
    RankDurationType,
    SearchType,
    TimelineType,
    V2EndpointsType,
    VideoFormatType,
    VideoQualityType,
)
from fastapi import Depends, Request
from utils.utils import SlashRouter, exclude_params

router = SlashRouter(tags=["Bilibili V2"])

BilibiliAPIRoot = NetRequest()


async def requestClient():
    async with BilibiliAPIRoot as client:
        yield BilibiliEndpointV2(client)


@router.get("/", summary="Bilibili API 兼容实现")
async def matchAll(
    request: Request,
    get: V2EndpointsType = V2EndpointsType.playurl,
    client: BilibiliEndpointV2 = Depends(requestClient),
):
    func: Callable[..., Coroutine] = getattr(client, get)
    return await func(**exclude_params(func, request.query_params))


@router.get(V2EndpointsType.playurl)
async def play_url(
    aid: int,
    page: Optional[int] = None,
    quality: VideoQualityType = VideoQualityType.VIDEO_480P,
    type: VideoFormatType = VideoFormatType.MP4,
    endpoint: BilibiliEndpointV2 = Depends(requestClient),
):
    return await endpoint.playurl(aid=aid, page=page, quality=quality, type=type)


@router.get(V2EndpointsType.seasoninfo)
async def seasoninfo(
    self, season_id: int, endpoint: BilibiliEndpointV2 = Depends(requestClient)
):
    return await endpoint.seasoninfo(season_id=season_id)


@router.get(V2EndpointsType.seasonrecommend)
async def seasonrecommend(
    season_id: int, endpoint: BilibiliEndpointV2 = Depends(requestClient)
):
    return await endpoint.seasonrecommend(season_id=season_id)


@router.get(V2EndpointsType.comments)
async def comments(
    aid: Optional[int] = None,
    season_id: Optional[int] = None,
    index: Optional[int] = None,
    sort: CommentSortType = CommentSortType.TIME,
    page: int = 1,
    pagesize: int = 20,
    endpoint: BilibiliEndpointV2 = Depends(requestClient),
):
    return await endpoint.comments(
        aid=aid,
        season_id=season_id,
        index=index,
        sort=sort,
        page=page,
        pagesize=pagesize,
    )


@router.get(V2EndpointsType.search)
async def search(
    keyword: str = "",
    type: SearchType = SearchType.search,
    page: int = 1,
    pagesize: int = 20,
    limit: int = 50,
    endpoint: BilibiliEndpointV2 = Depends(requestClient),
):
    return await endpoint.search(
        keyword=keyword, type=type, page=page, pagesize=pagesize, limit=limit
    )


@router.get(V2EndpointsType.rank)
async def rank(
    content: Union[RankContentType, RankBangumiType] = RankContentType.FULL_SITE,
    duration: RankDurationType = RankDurationType.THREE_DAY,
    new: bool = True,
    endpoint: BilibiliEndpointV2 = Depends(requestClient),
):
    return await endpoint.rank(content=content, duration=duration, new=new)


@router.get(V2EndpointsType.typedynamic)
async def typedynamic(endpoint: BilibiliEndpointV2 = Depends(requestClient)):
    return await endpoint.typedynamic()


@router.get(V2EndpointsType.recommend)
async def recommend(endpoint: BilibiliEndpointV2 = Depends(requestClient)):
    return await endpoint.recommend()


@router.get(V2EndpointsType.timeline)
async def timeline(
    type: TimelineType = TimelineType.GLOBAL,
    endpoint: BilibiliEndpointV2 = Depends(requestClient),
):
    return await endpoint.timeline(type=type)


@router.get(V2EndpointsType.space)
async def space(
    vmid: int,
    page: int = 1,
    pagesize: int = 10,
    endpoint: BilibiliEndpointV2 = Depends(requestClient),
):
    return await endpoint.space(vmid=vmid, page=page, pagesize=pagesize)


@router.get(V2EndpointsType.archive)
async def archive(
    vmid: int,
    page: int = 1,
    pagesize: int = 10,
    endpoint: BilibiliEndpointV2 = Depends(requestClient),
):
    return await endpoint.archive(vmid=vmid, page=page, pagesize=pagesize)


@router.get(V2EndpointsType.favlist)
async def favlist(
    fid: int,
    vmid: int,
    page: int = 1,
    pagesize: int = 20,
    endpoint: BilibiliEndpointV2 = Depends(requestClient),
):
    return await endpoint.favlist(fid=fid, vmid=vmid, page=page, pagesize=pagesize)
