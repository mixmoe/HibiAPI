from typing import Any

from hibiapi.utils.config import APIConfig

_Config = APIConfig("sauce")


class SauceConstants:
    CONFIG: APIConfig = _Config
    API_KEY: list[str] = _Config["net"]["api-key"].as_str_seq()
    USER_AGENT: str = _Config["net"]["user-agent"].as_str()
    PROXIES: dict[str, str] = _Config["proxy"].as_dict()
    IMAGE_HEADERS: dict[str, Any] = _Config["image"]["headers"].as_dict()
    IMAGE_ALLOWED_HOST: list[str] = _Config["image"]["allowed"].get(list[str])
    IMAGE_MAXIMUM_SIZE: int = _Config["image"]["max-size"].as_number() * 1024
    IMAGE_TIMEOUT: int = _Config["image"]["timeout"].as_number()
