from typing import Optional

from fastapi import Depends, Header

from hibiapi.api.pixiv import NetRequest, PixivConstants, PixivEndpoints
from hibiapi.utils.log import logger
from hibiapi.utils.routing import EndpointRouter

if not (refresh_tokens := PixivConstants.CONFIG["account"]["token"].as_str_seq()):
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
router.include_endpoint(PixivEndpoints, api_root := NetRequest(refresh_tokens))
