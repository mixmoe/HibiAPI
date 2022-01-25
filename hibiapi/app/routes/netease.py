from typing import Callable, Coroutine, List

from fastapi import Depends, Query, Request

from hibiapi.api.netease import (
    BitRateType,
    EndpointsType,
    NeteaseConstants,
    NeteaseEndpoint,
    NetRequest,
    RecordPeriodType,
    SearchType,
)
from hibiapi.utils.routing import SlashRouter, exclude_params

__mount__, __config__ = "netease", NeteaseConstants.CONFIG
router = SlashRouter(tags=["Netease"])

NeteaseAPIRoot = NetRequest()


async def request_client():
    async with NeteaseAPIRoot as client:
        yield NeteaseEndpoint(client)


@router.get("/", summary="网易云音乐 API 兼容实现", deprecated=True)
async def _match_all(
    request: Request,
    type: EndpointsType = EndpointsType.song,
    endpoint: NeteaseEndpoint = Depends(request_client),
):
    func: Callable[..., Coroutine] = getattr(endpoint, type)
    return await func(**exclude_params(func, request.query_params))


@router.get(EndpointsType.search)
async def search(
    s: str,
    search_type: SearchType = SearchType.SONG,
    limit: int = 20,
    offset: int = 0,
    endpoint: NeteaseEndpoint = Depends(request_client),
):
    """
    ## Name: `search`

    > 搜索

    ---

    ### Required:

    - ***str*** **`s`**
        - Description: 关键词

    ---

    ### Optional:
    - ***SearchType*** `search_type` = `SearchType.SONG`
        - Description: 搜索类型

    - ***int*** `limit` = `20`
        - Description: 指定返回结果数量

    - ***int*** `offset` = `0`
        - Description: 指定偏移数量，用于分页

    """
    return await endpoint.search(
        s=s,
        search_type=search_type,
        limit=limit,
        offset=offset,
    )


@router.get(EndpointsType.artist)
async def artist(id: int, endpoint: NeteaseEndpoint = Depends(request_client)):
    """
    ## Name: `artist`

    > 歌手

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 歌手ID

    """
    return await endpoint.artist(id=id)


@router.get(EndpointsType.album)
async def album(id: int, endpoint: NeteaseEndpoint = Depends(request_client)):
    """
    ## Name: `album`

    > 专辑

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 专辑ID

    """
    return await endpoint.album(id=id)


@router.get(EndpointsType.detail)
async def detail(
    id: List[int] = Query(...), endpoint: NeteaseEndpoint = Depends(request_client)
):
    """
    ## Name: `detail`

    > 歌曲详情

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 歌曲ID

    """
    return await endpoint.detail(id=id)


@router.get(EndpointsType.song)
async def song(
    id: List[int] = Query(...),
    br: BitRateType = BitRateType.STANDARD,
    endpoint: NeteaseEndpoint = Depends(request_client),
):
    """
    ## Name: `song`

    > 单曲

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 单曲ID

    ---

    ### Optional:
    - ***BitRateType*** `br` = `BitRateType.STANDARD`
        - Description: 歌曲码率

    """
    return await endpoint.song(id=id, br=br)


@router.get(EndpointsType.playlist)
async def playlist(id: int, endpoint: NeteaseEndpoint = Depends(request_client)):
    """
    ## Name: `playlist`

    > 歌单

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 歌单ID

    """
    return await endpoint.playlist(id=id)


@router.get(EndpointsType.lyric)
async def lyric(id: int, endpoint: NeteaseEndpoint = Depends(request_client)):
    """
    ## Name: `lyric`

    > 歌词

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 单曲ID

    """
    return await endpoint.lyric(id=id)


@router.get(EndpointsType.mv)
async def mv(id: int, endpoint: NeteaseEndpoint = Depends(request_client)):
    """
    ## Name: `mv`

    > MV

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: MVID

    """
    return await endpoint.mv(id=id)


@router.get(EndpointsType.comments)
async def comments(
    id: int,
    offset: int = 0,
    limit: int = 20,
    endpoint: NeteaseEndpoint = Depends(request_client),
):
    """
    ## Name: `comments`

    > 评论

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 单曲ID

    ---

    ### Optional:
    - ***int*** `offset` = `0`
        - Description: 指定偏移数量，用于分页
    - ***int*** `limit` = `20`
        - Description: 指定返回结果数量

    """
    return await endpoint.comments(
        id=id,
        offset=offset,
        limit=limit,
    )


@router.get(EndpointsType.record)
async def record(
    id: int,
    period: RecordPeriodType = RecordPeriodType.ALL,
    endpoint: NeteaseEndpoint = Depends(request_client),
):
    """
    ## Name: `record`

    > 听歌记录

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 用户ID

    ---

    ### Optional:
    - ***RecordPeriodType*** `period` = `RecordPeriodType.ALL`
        - Description: 听歌记录时段

    """
    return await endpoint.record(id=id, period=period)


@router.get(EndpointsType.djradio)
async def djradio(id: int, endpoint: NeteaseEndpoint = Depends(request_client)):
    """
    ## Name: `djradio`

    > 主播电台

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 电台ID

    """
    return await endpoint.djradio(id=id)


@router.get(EndpointsType.dj)
async def dj(
    id: int,
    offset: int = 0,
    limit: int = 20,
    asc: bool = False,
    endpoint: NeteaseEndpoint = Depends(request_client),
):
    """
    ## Name: `dj`

    > 主播电台单曲

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 电台单曲ID

    ---

    ### Optional:
    - ***int*** `offset` = `0`
        - Description: 指定偏移数量，用于分页

    - ***int*** `limit` = `20`
        - Description: 指定返回结果数量

    - ***bool*** `asc` = `False`
        - Description: 是否按升序排列

    """
    return await endpoint.dj(
        id=id,
        offset=offset,
        limit=limit,
        asc=asc,
    )


@router.get(EndpointsType.detail_dj)
async def detail_dj(id: int, endpoint: NeteaseEndpoint = Depends(request_client)):
    """
    ## Name: `detail_dj`

    > 主播电台歌曲详情

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 电台歌曲ID

    """
    return await endpoint.detail_dj(id=id)


@router.get(EndpointsType.user)
async def user(id: int, endpoint: NeteaseEndpoint = Depends(request_client)):
    """
    ## Name: `user`

    > 获取用户详细信息

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 用户ID

    """
    return await endpoint.user(id=id)


@router.get(EndpointsType.user_playlist)
async def user_playlist(
    id: int,
    offset: int = 0,
    limit: int = 20,
    endpoint: NeteaseEndpoint = Depends(request_client),
):
    """
    ## Name: `user_playlist`

    > 获取用户创建的歌单

    ---

    ### Required:

    - ***int*** **`id`**
        - Description: 用户ID

    ---

    ### Optional:
    - ***int*** `offset` = `0`
        - Description: 指定偏移数量，用于分页

    - ***int*** `limit` = `20`
        - Description: 指定返回结果数量

    """
    return await endpoint.user_playlist(
        id=id,
        offset=offset,
        limit=limit,
    )
