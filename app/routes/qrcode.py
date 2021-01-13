from typing import Optional

from api.qrcode import HostUrl, QRCodeLevel, QRInfo, ReturnEncode
from fastapi import Request, Response
from pydantic.color import Color
from utils.temp import TempFile
from utils.utils import SlashRouter

QR_CALLBACK_TEMPLATE = (
    r"""function {fun}(){document.write('<img class="qrcode" src="{url}"/>');}"""
)


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
    qr.url = TempFile.to_url(request, qr.path)  # type:ignore
    """function {fun}(){document.write('<img class="qrcode" src="{url}"/>');}"""
    return (
        qr
        if encode == ReturnEncode.json
        else Response(
            content=qr.json(),
            media_type="application/json",
            headers={"Location": qr.url},
            status_code=302,
        )
        if encode == ReturnEncode.raw
        else Response(
            content="{fun}({json})".format(json=qr.json(), fun=fun),
            media_type="text/javascript",
        )
        if encode == ReturnEncode.jsc
        else Response(
            content="function "
            + fun
            + '''(){document.write('<img class="qrcode" src="'''
            + qr.url
            + """"/>');}""",
            media_type="text/javascript",
        )
    )
