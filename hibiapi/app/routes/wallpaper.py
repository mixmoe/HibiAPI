from hibiapi.api.wallpaper import Config, NetRequest, WallpaperEndpoint
from hibiapi.utils.routing import EndpointRouter

__mount__, __config__ = "wallpaper", Config

router = EndpointRouter(tags=["Wallpaper"])
router.include_endpoint(WallpaperEndpoint, NetRequest())
