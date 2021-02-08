from httpx import Cookies
from utils.net import BaseNetClient

from .constants import NeteaseConstants


class NetRequest(BaseNetClient):
    def __init__(self):
        super().__init__(
            headers=NeteaseConstants.DEFAULT_HEADERS,
            cookies=Cookies({k: v.value for k, v in NeteaseConstants.COOKIES.items()}),
        )
