from hibiapi.api.tieba import Config, NetRequest, TiebaEndpoint
from hibiapi.utils.routing import EndpointRouter

__mount__, __config__ = "tieba", Config

router = EndpointRouter(tags=["Tieba"])
router.include_endpoint(TiebaEndpoint, NetRequest())
