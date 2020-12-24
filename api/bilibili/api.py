import hashlib
import json
from json.decoder import JSONDecodeError
from time import time
from typing import Any, Dict, Optional, overload

from httpx import URL, HTTPError, HTTPStatusError
from utils.exceptions import UpstreamAPIException
from utils.utils import BaseEndpoint

from .constants import BilibiliConstants


class BilibiliEndpointImplention(BaseEndpoint):
    def _sign(self, base: str, endpoint: str, params: Dict[str, Any]) -> URL:
        params.update(
            {
                **BilibiliConstants.DEFAULT_PARAMS,
                "access_key": BilibiliConstants.ACCESS_KEY,
                "appkey": BilibiliConstants.APP_KEY,
                "ts": int(time()),
            }
        )
        params = {k: params[k] for k in sorted(params.keys())}
        url = self._join(base=base, endpoint=endpoint, params=params)
        sign = hashlib.md5(
            string=(url.query + BilibiliConstants.SECRET.encode())
        ).hexdigest()
        return URL(url, params={"sign": sign})

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        content = content.replace("http:", "https:")
        try:
            return json.loads(content)
        except JSONDecodeError:
            right, left = content.find("("), content.rfind(")")
            return json.loads(content[right + 1 : left].strip())

    @overload
    async def request(
        self,
        endpoint: str,
        *,
        sign: bool = True,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ...

    @overload
    async def request(
        self,
        endpoint: str,
        path: str,
        *,
        sign: bool = True,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ...

    async def request(
        self,
        endpoint: str,
        path: Optional[str] = None,
        *,
        sign: bool = True,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        host, endpoint = (
            (BilibiliConstants.APP_HOST, endpoint)
            if path is None
            else (BilibiliConstants.SERVER_HOST[endpoint], path)
        )
        url = (
            self._join(base=host, endpoint=endpoint, params=params or {})
            if sign
            else self._sign(base=host, endpoint=endpoint, params=params or {})
        )
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return self._parse_json(response.text)
        except HTTPStatusError as e:
            raise UpstreamAPIException(detail=e.response.text)
        except HTTPError:
            raise UpstreamAPIException

    async def cid2url(self, *, cid: int, quality: int = 2, type: str = "hdmp4"):
        pass

    async def view(self, *, aid: int):
        return await self.request("x/v2/view", params={"aid": aid})

    async def search(self, *, keyword: str, page: int = 1, pagesize: int = 20):
        return await self.request(
            "x/v2/search",
            params={"duration": 0, "keyword": keyword, "pn": page, "ps": pagesize},
        )

    async def search_hot(self, *, limit: int = 50):
        return await self.request("x/v2/search/hot", params={"limit": limit})

    async def search_suggest(self, *, keyword: str, type: str = "accurate"):
        return await self.request(
            "x/v2/search/suggest", params={"keyword": keyword, "type": type}
        )

    async def space(self, *, vmid: int, pagesize: int = 10):
        return await self.request("x/v2/space", params={"vmid": vmid, "ps": pagesize})

    async def space_archive(self, *, vmid: int, page: int = 1, pagesize: int = 10):
        return await self.request(
            "x/v2/space/archive", params={"vmid": vmid, "ps": pagesize, "pn": page}
        )

    async def favorite_video(
        self,
        fid: int,
        vmid: int,
        order: str = "ftime",
        page: int = 1,
        pagesize: int = 20,
    ):
        return await self.request(
            "x/v2/fav/video",
            params={
                "fid": fid,
                "pn": page,
                "ps": pagesize,
                "vmid": vmid,
                "order": order,
            },
        )

    async def event_list(
        self,
        *,
        fid: int,
        vmid: int,
        order: str = "ftime",
        page: int = 1,
        pagesize: int = 20,
    ):
        return await self.request(
            "event/getlist",
            "api",
            params={
                "fid": fid,
                "pn": page,
                "ps": pagesize,
                "vmid": vmid,
                "order": order,
            },
        )

    async def season_info(self, *, season_id: int):
        return await self.request(
            "api/season_v5", "bgm", params={"season_id": season_id}
        )

    async def season_info_web(self, *, season_id: int):
        return await self.request(
            "jsonp/seasoninfo/{season_id}.ver",
            "bgm",
            sign=False,
            params={
                "callback": "seasonListCallback",
                "jsonp": "jsonp",
                "season_id": season_id,
                "_": int(time()),
            },
        )

    async def bangumi_source(self, *, episode_id: int):
        return await self.request(
            "api/get_source", "bgm", params={"episode_id": episode_id}
        )

    async def season_recommend(self, *, season_id: int):
        return await self.request(
            "api/season/recommend/rnd/{season_id}.json", params={"season_id": season_id}
        )

    async def comments(self, *, aid: int, sort: int = 0):
        return await self.request(
            "x/reply",
            "api",
            sign=False,
            params={"type": 1, "oid": aid, "pn": 1, "nohot": 1, "sort": sort},
        )

    async def rank_list(self, *, type: str = "all"):
        pass
