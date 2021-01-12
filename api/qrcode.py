from datetime import datetime
from enum import Enum
from fnmatch import fnmatch
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

from PIL import Image  # type:ignore
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    UrlHostError,
    conint,
    validate_arguments,
)
from pydantic.color import Color
from utils.config import APIConfig
from utils.decorators import ToAsync
from utils.exceptions import ClientSideException
from utils.temp import TempFile
from utils.utils import BaseNetClient

from qrcode import QRCode, constants  # type:ignore
from qrcode.image.pil import PilImage  # type:ignore

Config = APIConfig("qrcode")


class HostUrl(AnyHttpUrl):
    @classmethod
    def validate_host(
        cls, parts: Dict[str, str]
    ) -> Tuple[str, Optional[str], str, bool]:
        host, tld, host_type, rebuild = super().validate_host(parts)
        if not cls._check_domain(host):
            raise UrlHostError()
        return host, tld, host_type, rebuild

    @staticmethod
    def _check_domain(host: str) -> bool:
        return any(
            filter(
                lambda x: fnmatch(host, x),  # type:ignore
                Config["qrcode"]["icon-site"].get(List[str]),
            )
        )


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


class QRInfo(BaseModel):
    url: Optional[AnyHttpUrl] = None
    path: Path
    time: datetime = Field(default_factory=datetime.now)
    data: str
    logo: Optional[HostUrl] = None
    level: QRCodeLevel = QRCodeLevel.M
    size: int = 200  # type:ignore
    code: Literal[0] = 0
    status: Literal["success"] = "success"

    @classmethod
    @validate_arguments
    async def new(
        cls,
        text: str,
        *,
        size: conint(  # type:ignore
            strict=True,
            gt=Config["qrcode"]["min-size"].as_number(),  # noqa:F821
            lt=Config["qrcode"]["max-size"].as_number(),  # noqa:F821
        ) = 200,
        logo: Optional[HostUrl] = None,
        level: QRCodeLevel = QRCodeLevel.M,
        bgcolor: Color = Color("FFFFFF"),
        fgcolor: Color = Color("000000"),
    ):
        icon_stream = None
        if logo is not None:
            icon_stream = BytesIO()
            async with BaseNetClient() as client:
                response = await client.get(
                    logo, headers={"user-agent": "HibiAPI@GitHub"}, timeout=6
                )
                response.raise_for_status()
                icon_stream.write(response.content)
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
        level: QRCodeLevel = QRCodeLevel.M,
        icon_stream: Optional[BytesIO] = None,
        bgcolor: str = "#FFFFFF",
        fgcolor: str = "#000000",
    ) -> Path:
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
        if icon_stream is not None:
            try:
                icon = Image.open(icon_stream)
            except ValueError:
                raise ClientSideException("Invalid image format.")
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
        image.save(file := TempFile.create(ext=".png"))
        return file
