import hashlib
import json
from enum import Enum, IntEnum
from time import time
from typing import Any, Dict, Optional, overload

from httpx import URL, HTTPError, HTTPStatusError
from utils.exceptions import UpstreamAPIException
from utils.utils import BaseEndpoint

from ..constants import BilibiliConstants


class TimelineType(str, Enum):
    CN = "cn"
    GLOBAL = "global"


class CommentSortType(IntEnum):
    LIKES = 2
    HOT = 1
    TIME = 0


class CommentType(IntEnum):
    VIDEO = 1
    ARTICLE = 12
    DYNAMIC_PICTURE = 11
    DYNAMIC_TEXT = 17
    AUDIO = 14
    AUDIO_LIST = 19


class VideoQualityType(IntEnum):
    VIDEO_240P = 6
    VIDEO_360P = 16
    VIDEO_480P = 32
    VIDEO_720P = 64
    VIDEO_720P_60FPS = 74
    VIDEO_1080P = 80
    VIDEO_1080P_PLUS = 112
    VIDEO_1080P_60FPS = 116
    VIDEO_4K = 120


class VideoFormatType(IntEnum):
    FLV = 0
    MP4 = 2
    DASH = 16


class RankBangumiType(str, Enum):
    CN = "cn"
    GLOBAL = "global"


class RankContentType(IntEnum):
    FULL_SITE = 0  # 0 	全站
    DOUGA = 1  # 1 	动画
    GUOCHUANG = 168  # 168 	国创相关
    MUSIC = 3  # 3 	音乐
    DANCE = 129  # 129 	舞蹈
    GAME = 4  # 4 	游戏
    TECHNOLOGY = 36  # 36 	科技
    LIFE = 160  # 160 	生活
    KICHIKU = 119  # 119 	鬼畜
    FASHION = 155  # 155 	时尚
    INFORMATION = 165  # 165 	广告
    ENT = 5  # 5 	娱乐
    MOVIE = 23  # 23 	电影
    TV = 11  # 11 	电视剧


class RankDurationType(IntEnum):
    DAILY = 1
    THREE_DAY = 3
    WEEKLY = 7
    MONTHLY = 30


class BaseBilibiliEndpoint(BaseEndpoint):
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
        except json.JSONDecodeError:
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
        source: str,
        *,
        sign: bool = True,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ...

    async def request(
        self,
        endpoint: str,
        source: Optional[str] = None,
        *,
        sign: bool = True,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        host = (
            BilibiliConstants.APP_HOST
            if source is None
            else BilibiliConstants.SERVER_HOST[source]
        )
        url = (
            self._join(base=host, endpoint=endpoint, params=params or {})
            if not sign
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

    async def playurl(
        self,
        *,
        aid: int,
        cid: int,
        quality: VideoQualityType = VideoQualityType.VIDEO_480P,
        type: VideoFormatType = VideoFormatType.FLV,
    ):
        return await self.request(
            "x/player/playurl",
            "api",
            sign=False,
            params={
                "avid": aid,
                "cid": cid,
                "qn": quality,
                "fnval": type,
                "fnver": 0,
                "fourk": 0 if quality >= VideoQualityType.VIDEO_4K else 1,
            },
        )

    async def view(self, *, aid: int):
        return await self.request(
            "x/v2/view",
            params={
                "aid": aid,
            },
        )

    async def search(self, *, keyword: str, page: int = 1, pagesize: int = 20):
        return await self.request(
            "x/v2/search",
            params={
                "duration": 0,
                "keyword": keyword,
                "pn": page,
                "ps": pagesize,
            },
        )

    async def search_hot(self, *, limit: int = 50):
        return await self.request(
            "x/v2/search/hot",
            params={
                "limit": limit,
            },
        )

    async def search_suggest(self, *, keyword: str, type: str = "accurate"):
        return await self.request(
            "x/v2/search/suggest",
            params={
                "keyword": keyword,
                "type": type,
            },
        )

    async def space(self, *, vmid: int, page: int = 1, pagesize: int = 10):
        return await self.request(
            "x/v2/space",
            params={
                "vmid": vmid,
                "ps": pagesize,
                "pn": page,
            },
        )

    async def space_archive(self, *, vmid: int, page: int = 1, pagesize: int = 10):
        return await self.request(
            "x/v2/space/archive",
            params={
                "vmid": vmid,
                "ps": pagesize,
                "pn": page,
            },
        )

    async def favorite_video(
        self,
        fid: int,
        vmid: int,
        page: int = 1,
        pagesize: int = 20,
    ):
        return await self.request(
            "x/v2/fav/video",
            "api",
            params={
                "fid": fid,
                "pn": page,
                "ps": pagesize,
                "vmid": vmid,
                "order": "ftime",
            },
        )

    async def event_list(
        self,
        *,
        fid: int,
        vmid: int,
        page: int = 1,
        pagesize: int = 20,
    ):  # NOTE: this endpoint is not used
        return await self.request(
            "event/getlist",
            "api",
            params={
                "fid": fid,
                "pn": page,
                "ps": pagesize,
                "vmid": vmid,
                "order": "ftime",
            },
        )

    async def season_info(self, *, season_id: int):
        return await self.request(
            "api/season_v5",
            "bgm",
            params={
                "season_id": season_id,
            },
        )

    async def bangumi_source(self, *, episode_id: int):
        return await self.request(
            "api/get_source",
            "bgm",
            params={
                "episode_id": episode_id,
            },
        )

    async def season_recommend(self, *, season_id: int):
        return await self.request(
            "pgc/season/web/related/recommend",
            "api",
            sign=False,
            params={
                "season_id": season_id,
            },
        )

    async def comments(
        self,
        *,
        type: CommentType,
        oid: int,
        sort: CommentSortType = CommentSortType.TIME,
        page: int = 1,
        pagesize: int = 20,
    ):
        return await self.request(
            "x/v2/reply",
            "api",
            sign=False,
            params={
                "type": type,
                "oid": oid,
                "sort": sort,
                "pn": page,
                "ps": pagesize,
            },
        )

    async def rank_list_bangumi(
        self,
        *,
        site: RankBangumiType = RankBangumiType.GLOBAL,
        duration: RankDurationType = RankDurationType.THREE_DAY,
    ):
        return await self.request(
            "jsonp/season_rank_list/{site}/{duration}.ver",
            "bgm",
            sign=False,
            params={
                "duration": duration,
                "site": site,
            },
        )

    async def rank_list(
        self,
        content: RankContentType = RankContentType.FULL_SITE,
        duration: RankDurationType = RankDurationType.THREE_DAY,
        new: bool = True,
    ):
        return await self.request(
            "index/rank/all-{new_post}{duration}-{content}.json",
            "main",
            sign=False,
            params={
                "new_post": "" if new else "0",
                "duration": duration,
                "content": content,
            },
        )

    async def type_dynamic(self):
        return await self.request(
            "typedynamic/index",
            "api",
            sign=False,
            params={
                "type": "json",
            },
        )

    async def timeline(self, type: TimelineType = TimelineType.GLOBAL):
        return await self.request(
            "web_api/timeline_{type}",
            "bgm",
            sign=False,
            params={
                "type": type,
            },
        )

    async def recommend(self):
        return await self.request("index/recommend.json", "main", sign=False)

    async def suggest(self, *, keyword: str):  # NOTE: this endpoint is not used
        return await self.request(
            "main/suggest",
            "search",
            sign=False,
            params={
                "func": "suggest",
                "suggest_type": "accurate",
                "sug_type": "tag",
                "main_ver": "v1",
                "keyword": keyword,
            },
        )
