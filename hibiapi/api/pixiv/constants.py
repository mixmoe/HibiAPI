from typing import Any, Dict

from hibiapi.utils.config import APIConfig


class PixivConstants:
    DEFAULT_HEADERS: Dict[str, Any] = {
        "App-OS": "ios",
        "App-OS-Version": "14.6",
        "User-Agent": "PixivIOSApp/7.13.3 (iOS 14.6; iPhone13,2)",
    }
    CLIENT_ID: str = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
    CLIENT_SECRET: str = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
    HASH_SECRET: bytes = (
        b"28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c"
    )
    CONFIG: APIConfig = APIConfig("pixiv")
    APP_HOST: str = "https://app-api.pixiv.net"
    AUTH_HOST: str = "https://oauth.secure.pixiv.net"
