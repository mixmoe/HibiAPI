from fastapi import Depends, Header

from hibiapi.api.bika import (
    BikaConstants,
    BikaEndpoints,
    BikaLogin,
    ImageQuality,
    NetRequest,
)
from hibiapi.utils.log import logger
from hibiapi.utils.routing import EndpointRouter

try:
    BikaConstants.CONFIG["account"].get(BikaLogin)
except Exception as e:
    logger.warning(f"Bika account misconfigured: {e}")
    BikaConstants.CONFIG["enabled"].set(False)


async def x_image_quality(x_image_quality: ImageQuality = Header(ImageQuality.medium)):
    if x_image_quality is None:
        return BikaConstants.CONFIG["image_quality"].get(ImageQuality)
    return x_image_quality


__mount__, __config__ = "bika", BikaConstants.CONFIG
router = EndpointRouter(tags=["Bika"], dependencies=[Depends(x_image_quality)])

BikaAPIRoot = NetRequest()


router.include_endpoint(BikaEndpoints, BikaAPIRoot)
