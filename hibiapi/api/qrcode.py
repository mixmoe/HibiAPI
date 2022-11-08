from datetime import datetime
from enum import Enum
from io import BytesIO
from os import fdopen
from pathlib import Path
from typing import List, Literal, Optional, cast

from PIL import Image
from pydantic import AnyHttpUrl, BaseModel, Field, validate_arguments
from pydantic.color import Color
from qrcode import QRCode, constants
from qrcode.image.pil import PilImage

from hibiapi.utils.config import APIConfig
from hibiapi.utils.decorators import ToAsync, enum_auto_doc
from hibiapi.utils.exceptions import ClientSideException
from hibiapi.utils.net import BaseNetClient
from hibiapi.utils.routing import BaseHostUrl
from hibiapi.utils.temp import TempFile

Config = APIConfig("qrcode")


class HostUrl(BaseHostUrl):
    allowed_hosts = Config["qrcode"]["icon-site"].get(List[str])


@enum_auto_doc
class QRCodeLevel(str, Enum):
    """二维码容错率"""

    LOW = "L"
    """最低容错率"""
    MEDIUM = "M"
    """中等容错率"""
    QUARTILE = "Q"
    """高容错率"""
    HIGH = "H"
    """最高容错率"""


@enum_auto_doc
class ReturnEncode(str, Enum):
    """二维码返回的编码方式"""

    raw = "raw"
    """直接重定向到二维码图片"""
    json = "json"
    """返回JSON格式的二维码信息"""
    js = "js"
    jsc = "jsc"


class QRInfo(BaseModel):
    url: Optional[AnyHttpUrl] = None
    path: Path
    time: datetime = Field(default_factory=datetime.now)
    data: str
    logo: Optional[HostUrl] = None
    level: QRCodeLevel = QRCodeLevel.MEDIUM
    size: int = 200
    code: Literal[0] = 0
    status: Literal["success"] = "success"

    @classmethod
    @validate_arguments
    async def new(
        cls,
        text: str,
        *,
        size: int = Field(
            200,
            gt=Config["qrcode"]["min-size"].as_number(),
            lt=Config["qrcode"]["max-size"].as_number(),
        ),
        logo: Optional[HostUrl] = None,
        level: QRCodeLevel = QRCodeLevel.MEDIUM,
        bgcolor: Color = Color("FFFFFF"),
        fgcolor: Color = Color("000000"),
    ):
        icon_stream = None
        if logo is not None:
            async with BaseNetClient() as client:
                response = await client.get(
                    logo, headers={"user-agent": "HibiAPI@GitHub"}, timeout=6
                )
                response.raise_for_status()
            icon_stream = BytesIO(response.content)
        return cls(
            data=text,
            logo=logo,
            level=level,
            size=size,
            path=await cls._generate(
                text,
                size=size,
                level=level,
                icon_stream=icon_stream,
                bgcolor=bgcolor.as_hex(),
                fgcolor=fgcolor.as_hex(),
            ),
        )

    @classmethod
    @ToAsync
    def _generate(
        cls,
        text: str,
        *,
        size: int = 200,
        level: QRCodeLevel = QRCodeLevel.MEDIUM,
        icon_stream: Optional[BytesIO] = None,
        bgcolor: str = "#FFFFFF",
        fgcolor: str = "#000000",
    ) -> Path:
        qr = QRCode(
            error_correction={
                QRCodeLevel.LOW: constants.ERROR_CORRECT_L,
                QRCodeLevel.MEDIUM: constants.ERROR_CORRECT_M,
                QRCodeLevel.QUARTILE: constants.ERROR_CORRECT_Q,
                QRCodeLevel.HIGH: constants.ERROR_CORRECT_H,
            }[level],
            border=2,
            box_size=8,
        )
        qr.add_data(text)
        image = cast(
            Image.Image,
            qr.make_image(
                PilImage,
                back_color=bgcolor,
                fill_color=fgcolor,
            ).get_image(),
        )
        image = image.resize((size, size))
        if icon_stream is not None:
            try:
                icon = Image.open(icon_stream)
            except ValueError as e:
                raise ClientSideException("Invalid image format.") from e
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
        descriptor, path = TempFile.create(".png")
        with fdopen(descriptor, "wb") as f:
            image.save(f, format="PNG")
        return path
