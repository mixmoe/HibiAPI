from http.cookies import SimpleCookie
from typing import Any, Dict

from utils.config import APIConfig

_CONFIG = APIConfig("bilibili")


class BilibiliConstants:
    SERVER_HOST: Dict[str, str] = {
        "app": "https://app.bilibili.com",
        "api": "https://api.bilibili.com",
        "interface": "https://interface.bilibili.com",
        "main": "https://www.bilibili.com",
        "bgm": "https://bangumi.bilibili.com",
        "comment": "https://comment.bilibili.com",
        "search": "https://s.search.bilibili.com",
        "mobile": "https://m.bilibili.com",
    }
    APP_HOST: str = "http://app.bilibili.com"
    DEFAULT_PARAMS: Dict[str, Any] = {
        "build": 507000,
        "device": "android",
        "platform": "android",
        "mobi_app": "android",
    }
    APP_KEY: str = "1d8b6e7d45233436"
    SECRET: bytes = b"560c52ccd288fed045859ed18bffd973"
    ACCESS_KEY: str = "5271b2f0eb92f5f89af4dc39197d8e41"
    COOKIES: SimpleCookie = SimpleCookie(_CONFIG["net"]["cookie"].as_str())
    USER_AGENT: str = _CONFIG["net"]["user-agent"].as_str()
    CONFIG: APIConfig = _CONFIG
