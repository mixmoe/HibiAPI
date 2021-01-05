from typing import Optional
from urllib.parse import ParseResult

from api.qrcode import HostUrl, QRCodeLevel, QRInfo, ReturnEncode
from fastapi import Request, Response
from pydantic.color import Color
from utils.temp import TempFile
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
    response_model=QRInfo,
)
async def qrcode_api(
    request: Request,
    *,
    text: str,
    size: int = 200,
    logo: Optional[HostUrl] = None,
    encode: ReturnEncode = ReturnEncode.raw,
    level: QRCodeLevel = QRCodeLevel.M,
    bgcolor: Color = Color("FFFFFF"),
    fgcolor: Color = Color("000000"),
    fun: str = "qrcode",
):
    qr = await QRInfo.new(
        text, size=size, logo=logo, level=level, bgcolor=bgcolor, fgcolor=fgcolor
    )
    qr.url = ParseResult(  # type:ignore
        scheme=request.url.scheme,
        netloc=request.url.netloc,
        path=f"temp/{qr.path.relative_to(TempFile.path)}",
        params="",
        query="",
        fragment="",
    ).geturl()
    return (
        qr
        if encode == ReturnEncode.json
        else Response(headers={"Location": qr.url}, status_code=302)
        if encode == ReturnEncode.raw
        else Response(content=f"{fun}({qr.json()})", media_type="text/javascript")
    )
