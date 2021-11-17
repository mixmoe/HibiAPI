from hibiapi.utils.config import APIConfig

_CONFIG = APIConfig("wallpaper")


class WallpaperConstants:
    CONFIG: APIConfig = _CONFIG
    USER_AGENT: str = _CONFIG["net"]["user-agent"].as_str()
