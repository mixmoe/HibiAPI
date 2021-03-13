from typing import Callable, Coroutine

from api.bilibili import (
    BilibiliEndpointV3,
    CommentSortType,
    CommentType,
    NetRequest,
    RankBangumiType,
    RankContentType,
    RankDurationType,
    TimelineType,
    V3EndpointsType,
    VideoFormatType,
    VideoQualityType,
)
from fastapi import Depends, Request
from utils.routing import SlashRouter, exclude_params

router = SlashRouter(tags=["Bilibili V3"])

BilibiliAPIRoot = NetRequest()


async def requestClient():
    async with BilibiliAPIRoot as client:
        yield BilibiliEndpointV3(client)


@router.get("/", summary="整体实现")
async def matchAll(
    request: Request,
    get: V3EndpointsType = V3EndpointsType.video_info,
    client: BilibiliEndpointV3 = Depends(requestClient),
):
    func: Callable[..., Coroutine] = getattr(client, get)
    return await func(**exclude_params(func, request.query_params))


@router.get(V3EndpointsType.video_info)
async def video_info(aid: int, endpoint: BilibiliEndpointV3 = Depends(requestClient)):
    return await endpoint.video_info(aid=aid)


@router.get(V3EndpointsType.video_address)
async def video_address(
    aid: int,
    cid: int,
    quality: VideoQualityType = VideoQualityType.VIDEO_480P,
    type: VideoFormatType = VideoFormatType.FLV,
    endpoint: BilibiliEndpointV3 = Depends(requestClient),
):
    return await endpoint.video_address(aid=aid, cid=cid, quality=quality, type=type)


@router.get(V3EndpointsType.video_recommend)
async def video_recommend(endpoint: BilibiliEndpointV3 = Depends(requestClient)):
    return await endpoint.video_recommend()


@router.get(V3EndpointsType.video_dynamic)
async def video_dynamic(endpoint: BilibiliEndpointV3 = Depends(requestClient)):
    return await endpoint.video_dynamic()


@router.get(V3EndpointsType.video_ranking)
async def video_ranking(
    type: RankContentType = RankContentType.FULL_SITE,
    duration: RankDurationType = RankDurationType.THREE_DAY,
    endpoint: BilibiliEndpointV3 = Depends(requestClient),
):
    return await endpoint.video_ranking(type=type, duration=duration)


@router.get(V3EndpointsType.user_info)
async def user_info(
    uid: int,
    page: int = 1,
    size: int = 10,
    endpoint: BilibiliEndpointV3 = Depends(requestClient),
):
    return await endpoint.user_info(uid=uid, page=page, size=size)


@router.get(V3EndpointsType.user_uploaded)
async def user_uploaded(
    uid: int,
    page: int = 1,
    size: int = 10,
    endpoint: BilibiliEndpointV3 = Depends(requestClient),
):
    return await endpoint.user_uploaded(uid=uid, page=page, size=size)


@router.get(V3EndpointsType.user_favorite)
async def user_favorite(
    uid: int,
    fid: int,
    page: int = 1,
    size: int = 10,
    endpoint: BilibiliEndpointV3 = Depends(requestClient),
):
    return await endpoint.user_favorite(fid=fid, uid=uid, page=page, size=size)


@router.get(V3EndpointsType.season_info)
async def season_info(
    season_id: int, endpoint: BilibiliEndpointV3 = Depends(requestClient)
):
    return await endpoint.season_info(season_id=season_id)


@router.get(V3EndpointsType.season_recommend)
async def season_recommend(
    season_id: int, endpoint: BilibiliEndpointV3 = Depends(requestClient)
):
    return await endpoint.season_recommend(season_id=season_id)


@router.get(V3EndpointsType.season_episode)
async def season_episode(
    episode_id: int, endpoint: BilibiliEndpointV3 = Depends(requestClient)
):
    return await endpoint.season_episode(episode_id=episode_id)


@router.get(V3EndpointsType.season_timeline)
async def season_timeline(
    type: TimelineType = TimelineType.GLOBAL,
    endpoint: BilibiliEndpointV3 = Depends(requestClient),
):
    return await endpoint.season_timeline(type=type)


@router.get(V3EndpointsType.season_ranking)
async def season_ranking(
    type: RankBangumiType = RankBangumiType.GLOBAL,
    duration: RankDurationType = RankDurationType.THREE_DAY,
    endpoint: BilibiliEndpointV3 = Depends(requestClient),
):
    return await endpoint.season_ranking(type=type, duration=duration)


@router.get(V3EndpointsType.search)
async def search(
    keyword: str,
    page: int = 1,
    size: int = 20,
    endpoint: BilibiliEndpointV3 = Depends(requestClient),
):
    return await endpoint.search(keyword=keyword, page=page, size=size)


@router.get(V3EndpointsType.search_recommend)
async def search_recommend(
    limit: int = 50, endpoint: BilibiliEndpointV3 = Depends(requestClient)
):
    return await endpoint.search_recommend(limit=limit)


@router.get(V3EndpointsType.search_suggestion)
async def search_suggestion(
    keyword: str, endpoint: BilibiliEndpointV3 = Depends(requestClient)
):
    return await endpoint.search_suggestion(keyword=keyword)


@router.get(V3EndpointsType.comments)
async def comments(
    id: int,
    type: CommentType = CommentType.VIDEO,
    sort: CommentSortType = CommentSortType.TIME,
    page: int = 1,
    size: int = 20,
    endpoint: BilibiliEndpointV3 = Depends(requestClient),
):
    return await endpoint.comments(id=id, type=type, sort=sort, page=page, size=size)
