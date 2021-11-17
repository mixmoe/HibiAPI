from hibiapi.utils.net import BaseNetClient

from .constants import WallpaperConstants


class NetRequest(BaseNetClient):
    def __init__(self):
        super().__init__(headers={"user-agent": WallpaperConstants.USER_AGENT})
