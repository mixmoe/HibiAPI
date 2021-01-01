from typing import Callable, Coroutine

from api.bilibili import BilibiliEndpointV2, NetRequest, V2EndpointsType
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
