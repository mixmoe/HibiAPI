from typing import Any, Dict, List

from utils.config import APIConfig

_Config = APIConfig("sauce")


class SauceConstants:
    CONFIG: APIConfig = _Config
    API_KEY: str = _Config["net"]["api-key"].as_str()
    USER_AGENT: str = _Config["net"]["user-agent"].as_str()
    PROXIES: Dict[str, str] = _Config["proxy"].as_dict()
    IMAGE_HEADERS: Dict[str, Any] = _Config["image"]["headers"].as_dict()
    IMAGE_ALLOWED_HOST: List[str] = _Config["image"]["allowed"].get(List[str])
    IMAGE_MAXIMUM_SIZE: int = _Config["image"]["max-size"].as_number() * 1024
    IMAGE_TIMEOUT: int = _Config["image"]["timeout"].as_number()
