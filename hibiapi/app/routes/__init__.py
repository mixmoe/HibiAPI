from typing import List, Protocol, cast

from hibiapi.utils.config import APIConfig
from hibiapi.utils.exceptions import ExceptionReturn
from hibiapi.utils.log import logger
from hibiapi.utils.routing import SlashRouter

from . import bilibili, netease, pixiv, qrcode, sauce, tieba

router = SlashRouter(
    responses={
        code: {
            "model": ExceptionReturn,
        }
        for code in (400, 422, 500, 502)
    }
)


class RouteInterface(Protocol):
    router: SlashRouter
    __mount__: str
    __config__: APIConfig


modules = cast(List[RouteInterface], [bilibili, netease, pixiv, qrcode, sauce, tieba])

for module in modules:
    mount = (
        mountpoint
        if (mountpoint := module.__mount__).startswith("/")
        else ("/" + mountpoint)
    )
    if not module.__config__["enabled"].as_bool():
        logger.warning(
            f"API Route <y><b>{mount}</b></y> has been <r><b>disabled</b></r> in config."
        )
        continue
    router.include_router(module.router, prefix=mount)
