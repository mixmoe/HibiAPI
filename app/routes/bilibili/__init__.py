from utils.utils import SlashRouter

from .v2 import router as RouterV2
from .v3 import router as RouterV3

router = SlashRouter()
router.include_router(RouterV2, prefix="/v2")
router.include_router(RouterV3, prefix="/v3")
