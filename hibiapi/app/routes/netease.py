from hibiapi.api.netease import NeteaseConstants, NeteaseEndpoint, NetRequest
from hibiapi.utils.routing import EndpointRouter

__mount__, __config__ = "netease", NeteaseConstants.CONFIG

router = EndpointRouter(tags=["Netease"])
router.include_endpoint(NeteaseEndpoint, NetRequest())
