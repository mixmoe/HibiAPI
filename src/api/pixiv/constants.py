from typing import Any, Dict

from utils.config import APIConfig


class PixivConstants:
    DEFAULT_HEADERS: Dict[str, Any] = {
        "App-OS": "ios",
        "App-OS-Version": "12.2",
        "App-Version": "7.6.2",
        "User-Agent": "PixivIOSApp/7.6.2 (iOS 12.2; iPhone9,1)",
    }
    CLIENT_ID: str = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
    CLIENT_SECRET: str = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
    HASH_SECRET: bytes = (
        b"28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c"
    )
    CONFIG: APIConfig = APIConfig("pixiv")
    APP_HOST: str = "https://app-api.pixiv.net"
    PUB_HOST: str = "https://public-api.secure.pixiv.net"
    AUTH_HOST: str = "https://oauth.secure.pixiv.net"
