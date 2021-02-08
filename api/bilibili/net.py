from httpx import Cookies
from utils.net import BaseNetClient

from .constants import BilibiliConstants


class NetRequest(BaseNetClient):
    def __init__(self):
        super().__init__(
            headers={"user-agent": BilibiliConstants.USER_AGENT},
            cookies=Cookies({k: v.value for k, v in BilibiliConstants.COOKIES.items()}),
        )
