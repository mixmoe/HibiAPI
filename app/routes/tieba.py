from typing import Callable, Coroutine

from api.tieba import EndpointsType, NetRequest, TiebaEndpoint
from fastapi import Depends, Request
from utils.utils import SlashRouter, exclude_params

TiebaAPIRoot = NetRequest()
router = SlashRouter(tags=["Tieba"])


async def requestClient():
    async with TiebaAPIRoot as client:
        yield TiebaEndpoint(client)


@router.get("/")
async def matchAll(
    request: Request,
    type: EndpointsType = EndpointsType.post_detail,
    endpoint: TiebaEndpoint = Depends(requestClient),
):
    func: Callable[..., Coroutine] = getattr(endpoint, type)
    return await func(**exclude_params(func, request.query_params))


@router.get(EndpointsType.post_list)
async def post_list(
    name: str,
    page: int = 1,
    size: int = 50,
    endpoint: TiebaEndpoint = Depends(requestClient),
):
    return await endpoint.post_list(name=name, page=page, size=size)


@router.get(EndpointsType.post_detail)
async def post_detail(
    tid: int,
    page: int = 1,
    size: int = 50,
    reversed: bool = False,
    endpoint: TiebaEndpoint = Depends(requestClient),
):
    return await endpoint.post_detail(tid=tid, page=page, size=size, reversed=reversed)


@router.get(EndpointsType.subpost_detail)
async def subpost_detail(
    tid: int,
    pid: int,
    page: int = 1,
    size: int = 50,
    endpoint: TiebaEndpoint = Depends(requestClient),
):
    return await endpoint.subpost_detail(tid=tid, pid=pid, page=page, size=size)


@router.get(EndpointsType.user_profile)
async def user_profile(uid: int, endpoint: TiebaEndpoint = Depends(requestClient)):
    return await endpoint.user_profile(uid=uid)


@router.get(EndpointsType.user_subscribed)
async def user_subscribed(uid: int, endpoint: TiebaEndpoint = Depends(requestClient)):
    return await endpoint.user_subscribed(uid=uid)
