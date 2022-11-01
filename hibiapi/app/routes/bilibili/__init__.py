from hibiapi.api.bilibili import BilibiliConstants
from hibiapi.app.routes.bilibili.v2 import router as RouterV2
from hibiapi.app.routes.bilibili.v3 import router as RouterV3
from hibiapi.utils.routing import SlashRouter

__mount__, __config__ = "bilibili", BilibiliConstants.CONFIG

router = SlashRouter()
router.include_router(RouterV2, prefix="/v2")
router.include_router(RouterV3, prefix="/v3")
