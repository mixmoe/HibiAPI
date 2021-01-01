from typing import Callable, Coroutine

from api.bilibili import BilibiliEndpointV3, NetRequest, V3EndpointsType
from fastapi import Depends, Request
from utils.utils import SlashRouter, exclude_params

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
