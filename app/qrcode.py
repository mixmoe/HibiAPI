from typing import Optional

from api.qrcode import QRCodeLevel, ReturnEncode, qrcode
from pydantic import HttpUrl
from utils.utils import SlashRouter

router = SlashRouter(tags=["QRCode"])


@router.get(
    "/",
    responses={
        200: {
            "content": {"image/png": {}, "text/javascript": {}, "application/json": {}},
            "description": "Avaliable to return an javascript, image or json.",
        }
    },
)
async def qrcode_api(
    text: str,
    size: int = 200,
    icon: Optional[HttpUrl] = None,
    encode: ReturnEncode = ReturnEncode.raw,
    level: QRCodeLevel = QRCodeLevel.M,
    bgcolor: str = "#FFFFFF",
    fgcolor: str = "#000000",
):
    return await qrcode(
        text,
        size=size,
        icon=icon,
        encode=encode,
        level=level,
        fgcolor=fgcolor,
        bgcolor=bgcolor,
    )
