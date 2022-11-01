import asyncio
from typing import Optional

from fastapi import Depends, Header

from hibiapi.api.pixiv import NetRequest, PixivConstants, PixivEndpoints
from hibiapi.utils.log import logger
from hibiapi.utils.routing import EndpointRouter

if not PixivConstants.CONFIG["account"]["token"].get():
    logger.warning("Pixiv API token is not set, pixiv endpoint will be unavailable.")
    PixivConstants.CONFIG["enabled"].set(False)


async def accept_language(
    accept_language: Optional[str] = Header(
        None,
        description="Accepted tag translation language",
    )
):
    return accept_language


__mount__, __config__ = "pixiv", PixivConstants.CONFIG

router = EndpointRouter(tags=["Pixiv"], dependencies=[Depends(accept_language)])
router.include_endpoint(PixivEndpoints, api_root := NetRequest())


@router.on_event("startup")
async def login():
    logger.debug("Trying to refresh Pixiv account identity.")

    asyncio.get_running_loop().call_later(
        PixivConstants.REFRESH_INTERVAL,
        callback=lambda: asyncio.ensure_future(login()),
    )

    try:
        await api_root.login()
    except Exception:
        logger.error("Error occurred during logging to Pixiv account:")
        raise

    return
