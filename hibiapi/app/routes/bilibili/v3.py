from hibiapi.api.bilibili import BilibiliEndpointV3, NetRequest
from hibiapi.utils.routing import EndpointRouter

router = EndpointRouter(tags=["Bilibili V3"])
router.include_endpoint(BilibiliEndpointV3, NetRequest())
