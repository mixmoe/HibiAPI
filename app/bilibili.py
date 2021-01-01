from typing import Callable, Coroutine

from api.bilibili import BilibiliEndpointV2, NetRequest
from fastapi import Depends, Request
from utils.utils import SlashRouter, exclude_params

router = SlashRouter(tags=["Bilibili"])

BilibiliAPIRoot = NetRequest()


async def requestClient():
    async with BilibiliAPIRoot as client:
        yield BilibiliEndpointV2(client)


@router.get("/")
async def matchAll(
    request: Request,
    get: str = "playurl",
    client: BilibiliEndpointV2 = Depends(requestClient),
):
    func: Callable[..., Coroutine] = getattr(client, get)
    return await func(**exclude_params(func, request.query_params))
