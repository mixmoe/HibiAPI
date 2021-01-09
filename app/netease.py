from typing import Callable, Coroutine

from api.netease import NeteaseEndpoint, NetRequest
from fastapi import Depends, Request
from utils.utils import SlashRouter, exclude_params

router = SlashRouter(tags=["Netease"])

NeteaseAPIRoot = NetRequest()


async def requestClient():
    async with NeteaseAPIRoot as client:
        yield NeteaseEndpoint(client)


@router.get("/")
async def matchAll(
    request: Request,
    get: str,
    endpoint: NeteaseEndpoint = Depends(requestClient),
):
    func: Callable[..., Coroutine] = getattr(endpoint, get)
    return await func(**exclude_params(func, request.query_params))
