import hashlib
from time import time
from typing import Any, Dict, Optional

from httpx import URL, HTTPError, HTTPStatusError
from utils.decorators import ToAsync
from utils.exceptions import UpstreamAPIException
from utils.utils import BaseEndpoint

from .constants import BilibiliConstants


class BilibiliEndpoint(BaseEndpoint):
    @ToAsync
    def _sign(self, endpoint: str, params: Dict[str, Any]) -> URL:
        params.update(
            {
                **BilibiliConstants.DEFAULT_PARAMS,
                "access_key": BilibiliConstants.ACCESS_KEY,
                "appkey": BilibiliConstants.APP_KEY,
                "ts": int(time()),
            }
        )
        params = {k: params[k] for k in sorted(params.keys())}
        url = self._join(BilibiliConstants.APP_HOST, endpoint, params)
        sign = hashlib.md5(
            string=(url.query + BilibiliConstants.SECRET.encode())
        ).hexdigest()
        return URL(url, params={"sign": sign})

    async def request(
        self, endpoint: str, *, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = await self._sign(endpoint=endpoint, params=params or {})
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as e:
            raise UpstreamAPIException(detail=e.response.text)
        except HTTPError:
            raise UpstreamAPIException

    async def playurl(self, *, aid: int):
        return await self.request("x/v2/view", params={"aid": aid})
