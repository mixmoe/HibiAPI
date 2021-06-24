from http.cookies import SimpleCookie
from ipaddress import IPv4Address, IPv4Network
from random import randint
from typing import Dict

from hibiapi.utils.config import APIConfig

_Config = APIConfig("netease")


class NeteaseConstants:
    AES_KEY: bytes = b"0CoJUm6Qyw8W8jud"
    AES_IV: bytes = b"0102030405060708"
    RSA_PUBKEY: int = int("010001", 16)
    RSA_MODULUS: int = int(
        "00e0b509f6259df8642dbc3566290147"
        "7df22677ec152b5ff68ace615bb7b725"
        "152b3ab17a876aea8a5aa76d2e417629"
        "ec4ee341f56135fccf695280104e0312"
        "ecbda92557c93870114af6c9d05c4f7f"
        "0c3685b7a46bee255932575cce10b424"
        "d813cfe4875d3e82047b97ddef52741d"
        "546b8e289dc6935b3ece0462db0a22b8e7",
        16,
    )

    HOST: str = "http://music.163.com"
    COOKIES: SimpleCookie = SimpleCookie(_Config["net"]["cookie"].as_str())
    SOURCE_IP_SEGMENT: IPv4Network = _Config["net"]["source"].get(IPv4Network)
    DEFAULT_HEADERS: Dict[str, str] = {
        "user-agent": _Config["net"]["user-agent"].as_str(),
        "referer": "http://music.163.com",
        "x-real-ip": str(  # random a ip address from a specificed network segment
            IPv4Address(
                randint(
                    int(SOURCE_IP_SEGMENT.network_address),
                    int(SOURCE_IP_SEGMENT.broadcast_address),
                )
            )
        ),
    }

    CONFIG: APIConfig = _Config
