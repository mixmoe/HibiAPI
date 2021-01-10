from typing import Callable, Coroutine

from api.netease import (
    BitRateType,
    EndpointsType,
    NeteaseEndpoint,
    NetRequest,
    RecordPeriodType,
    SearchType,
)
from fastapi import Depends, Request
from utils.utils import SlashRouter, exclude_params

router = SlashRouter(tags=["Netease"])

NeteaseAPIRoot = NetRequest()


async def requestClient():
    async with NeteaseAPIRoot as client:
        yield NeteaseEndpoint(client)


@router.get("/", summary="网易云音乐 API 兼容实现")
async def matchAll(
    request: Request,
    type: EndpointsType = EndpointsType.song,
    endpoint: NeteaseEndpoint = Depends(requestClient),
):
    func: Callable[..., Coroutine] = getattr(endpoint, type)
    return await func(**exclude_params(func, request.query_params))


@router.get(EndpointsType.search)
async def search(
    s: str,
    search_type: SearchType = SearchType.SONG,
    limit: int = 20,
    offset: int = 0,
    endpoint: NeteaseEndpoint = Depends(requestClient),
):
    return await endpoint.search(
        s=s,
        search_type=search_type,
        limit=limit,
        offset=offset,
    )


@router.get(EndpointsType.artist)
async def artist(id: int, endpoint: NeteaseEndpoint = Depends(requestClient)):
    return await endpoint.artist(id=id)


@router.get(EndpointsType.album)
async def album(id: int, endpoint: NeteaseEndpoint = Depends(requestClient)):
    return await endpoint.album(id=id)


@router.get(EndpointsType.detail)
async def detail(id: int, endpoint: NeteaseEndpoint = Depends(requestClient)):
    return await endpoint.detail(id=id)


@router.get(EndpointsType.song)
async def song(
    id: int,
    br: BitRateType = BitRateType.STANDARD,
    endpoint: NeteaseEndpoint = Depends(requestClient),
):
    return await endpoint.song(id=id, br=br)


@router.get(EndpointsType.playlist)
async def playlist(id: int, endpoint: NeteaseEndpoint = Depends(requestClient)):
    return await endpoint.playlist(id=id)


@router.get(EndpointsType.lyric)
async def lyric(id: int, endpoint: NeteaseEndpoint = Depends(requestClient)):
    return await endpoint.lyric(id=id)


@router.get(EndpointsType.mv)
async def mv(id: int, endpoint: NeteaseEndpoint = Depends(requestClient)):
    return await endpoint.mv(id=id)


@router.get(EndpointsType.comments)
async def comments(
    id: int,
    offset: int = 0,
    limit: int = 20,
    endpoint: NeteaseEndpoint = Depends(requestClient),
):
    return await endpoint.comments(
        id=id,
        offset=offset,
        limit=limit,
    )


@router.get(EndpointsType.record)
async def record(
    id: int,
    period: RecordPeriodType = RecordPeriodType.ALL,
    endpoint: NeteaseEndpoint = Depends(requestClient),
):
    return await endpoint.record(id=id, period=period)


@router.get(EndpointsType.djradio)
async def djradio(id: int, endpoint: NeteaseEndpoint = Depends(requestClient)):
    return await endpoint.djradio(id=id)


@router.get(EndpointsType.dj)
async def dj(
    id: int,
    offset: int = 0,
    limit: int = 20,
    asc: bool = False,
    endpoint: NeteaseEndpoint = Depends(requestClient),
):
    return await endpoint.dj(
        id=id,
        offset=offset,
        limit=limit,
        asc=asc,
    )


@router.get(EndpointsType.detail_dj)
async def detail_dj(id: int, endpoint: NeteaseEndpoint = Depends(requestClient)):
    return await endpoint.detail_dj(id=id)
