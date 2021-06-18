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

modules = [bilibili, netease, pixiv, qrcode, sauce, tieba]

for module in modules:
    route: SlashRouter = getattr(module, "router")
    mount: str = getattr(module, "__mount__")
    config: APIConfig = getattr(module, "__config__")
    mount = mount if mount.startswith("/") else ("/" + mount)
    if not config["enabled"].as_bool():
        logger.warning(
            f"API Route <y><b>{mount}</b></y> <e>{route}</e> "
            "has been <r><b>disabled</b></r> in config."
        )
        continue
    router.include_router(route, prefix=mount)
