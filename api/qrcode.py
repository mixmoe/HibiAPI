from enum import Enum
from io import BytesIO
from typing import Optional

from fastapi.responses import StreamingResponse
from PIL import Image  # type:ignore
from utils.decorators import ToAsync
from utils.utils import BaseNetClient

from qrcode import QRCode, constants  # type:ignore
from qrcode.image.pil import PilImage  # type:ignore


class QRCodeLevel(str, Enum):
    L = "L"
    M = "M"
    Q = "Q"
    H = "H"


class ReturnEncode(str, Enum):
    raw = "raw"
    json = "json"
    js = "js"
    jsc = "jsc"


@ToAsync
def generate_qrcode(
    text: str,
    *,
    size: int = 200,
    level: QRCodeLevel = QRCodeLevel.M,
    icon_stream: Optional[BytesIO] = None,
    bgcolor: str = "#FFFFFF",
    fgcolor: str = "#000000"
):
    qr = QRCode(
        error_correction={
            QRCodeLevel.L: constants.ERROR_CORRECT_L,
            QRCodeLevel.M: constants.ERROR_CORRECT_M,
            QRCodeLevel.Q: constants.ERROR_CORRECT_Q,
            QRCodeLevel.H: constants.ERROR_CORRECT_H,
        }[level],
        border=2,
        box_size=8,
    )
    qr.add_data(text)
    image: Image.Image = qr.make_image(
        PilImage,
        back_color=bgcolor,
        fill_color=fgcolor,
    ).get_image()  # type:ignore
    image = image.resize((size, size))
    if icon_stream is None:
        return image
    icon = Image.open(icon_stream)
    icon_width, icon_height = icon.size
    image.paste(
        icon,
        box=(
            int(size / 2 - icon_width / 2),
            int(size / 2 - icon_height / 2),
            int(size / 2 + icon_width / 2),
            int(size / 2 + icon_height / 2),
        ),
        mask=icon if icon.mode == "RGBA" else None,
    )
    return image


async def qrcode(
    text: str,
    size: int = 200,
    icon: Optional[str] = None,
    encode: ReturnEncode = ReturnEncode.raw,
    level: QRCodeLevel = QRCodeLevel.M,
    bgcolor: str = "#FFFFFF",
    fgcolor: str = "#000000",
):
    icon_stream = None
    if icon is not None:
        icon_stream = BytesIO()
        async with BaseNetClient() as client:
            response = await client.get(
                icon, headers={"user-agent": "HibiAPI@GitHub"}, timeout=6
            )
            response.raise_for_status()
            icon_stream.write(response.content)
    qr = await generate_qrcode(
        text,
        size=size,
        level=level,
        bgcolor=bgcolor,
        fgcolor=fgcolor,
        icon_stream=icon_stream,
    )
    stream = BytesIO()
    qr.save(stream, "PNG")
    stream.seek(0)
    return StreamingResponse(content=stream, media_type="image/png")
