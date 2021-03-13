from utils.net import BaseNetClient

from .constants import SauceConstants


class NetRequest(BaseNetClient):
    def __init__(self):
        super().__init__(
            headers={"user-agent": SauceConstants.USER_AGENT},
            proxies=SauceConstants.PROXIES,  # type:ignore
        )
