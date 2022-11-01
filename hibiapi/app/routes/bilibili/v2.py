from hibiapi.api.bilibili.api import BilibiliEndpointV2
from hibiapi.api.bilibili.net import NetRequest
from hibiapi.utils.routing import EndpointRouter

router = EndpointRouter(tags=["Bilibili V2"])
router.include_endpoint(BilibiliEndpointV2, NetRequest())
