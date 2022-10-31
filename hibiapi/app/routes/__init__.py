from typing import List, Protocol, cast

from hibiapi.app.routes import (
    bika,
    bilibili,
    netease,
    pixiv,
    qrcode,
    sauce,
    tieba,
    wallpaper,
)
from hibiapi.utils.config import APIConfig
from hibiapi.utils.exceptions import ExceptionReturn
from hibiapi.utils.log import logger
from hibiapi.utils.routing import SlashRouter

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


modules = cast(
    List[RouteInterface],
    [bilibili, netease, pixiv, qrcode, sauce, tieba, wallpaper, bika],
)

for module in modules:
    mount = (
        mount_point
        if (mount_point := module.__mount__).startswith("/")
        else f"/{mount_point}"
    )

    if not module.__config__["enabled"].as_bool():
        logger.warning(
            f"API Route <y><b>{mount}</b></y> has been <r><b>disabled</b></r> in config."
        )
        continue
    router.include_router(module.router, prefix=mount)
