import asyncio
from typing import Callable, Coroutine, NoReturn

from api.pixiv import PixivAPI, PixivEndpoints
from api.pixiv.constants import PixivConstants
from fastapi import APIRouter, Depends, Request
from utils.log import logger

router = APIRouter()


PixivAPIRoot = PixivAPI()


async def requestClient():
    async with PixivAPIRoot.net as client:
        yield PixivEndpoints(client)


@router.on_event("startup")
async def login():
    async def _refreshIdentity() -> NoReturn:
        while True:
            logger.info("Start trying to login pixiv account")
            try:
                await PixivAPIRoot.login()
            except Exception:
                logger.exception("Exception occurred during trying to login account:")
            await asyncio.sleep(
                PixivConstants.CONFIG["account"]["refresh_interval"].as_number()
            )

    asyncio.ensure_future(_refreshIdentity())


@router.get("/")
async def matchAll(
    request: Request,
    type: str = "illust",
    endpoint: PixivEndpoints = Depends(requestClient),
):
    func: Callable[..., Coroutine] = getattr(endpoint, type)
    params = {**request.query_params}
    if "type" in params:
        params.pop("type")
    return await func(**params)
