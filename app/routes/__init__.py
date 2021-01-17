from utils.exceptions import ExceptionReturn
from utils.utils import SlashRouter

from .bilibili import router as BilibiliRouter
from .netease import router as NeteaseRouter
from .pixiv import router as PixivRouter
from .qrcode import router as QRCodeRouter
from .tieba import router as TiebaRouter

router = SlashRouter(
    responses={
        code: {
            "model": ExceptionReturn,
        }
        for code in (400, 422, 500, 502)
    }
)
router.include_router(PixivRouter, prefix="/pixiv")
router.include_router(BilibiliRouter, prefix="/bilibili")
router.include_router(QRCodeRouter, prefix="/qrcode")
router.include_router(NeteaseRouter, prefix="/netease")
router.include_router(TiebaRouter, prefix="/tieba")
