import random
from enum import IntEnum
from io import BytesIO
from typing import Any, Dict, Optional, overload

from httpx import HTTPError

from hibiapi.api.sauce.constants import SauceConstants
from hibiapi.utils.decorators import enum_auto_doc
from hibiapi.utils.exceptions import ClientSideException
from hibiapi.utils.net import catch_network_error
from hibiapi.utils.routing import BaseEndpoint, BaseHostUrl


class UnavailableSourceException(ClientSideException):
    code = 422
    detail = "given image is not avaliable to fetch"


class ImageSourceOversizedException(UnavailableSourceException):
    code = 413
    detail = (
        "given image size is rather than maximum limit "
        f"{SauceConstants.IMAGE_MAXIMUM_SIZE} bytes"
    )


class HostUrl(BaseHostUrl):
    allowed_hosts = SauceConstants.IMAGE_ALLOWED_HOST


class UploadFileIO(BytesIO):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> BytesIO:
        if not isinstance(v, BytesIO):
            raise ValueError(f"Expected UploadFile, received: {type(v)}")
        return v


@enum_auto_doc
class DeduplicateType(IntEnum):
    DISABLED = 0
    """no result deduplicating"""
    IDENTIFIER = 1
    """consolidate search results and deduplicate by item identifier"""
    ALL = 2
    """all implemented deduplicate methods such as by series name"""


class SauceEndpoint(BaseEndpoint, cache_endpoints=False):
    base = "https://saucenao.com"

    async def fetch(self, host: HostUrl) -> UploadFileIO:
        try:
            response = await self.client.get(
                url=host,
                headers=SauceConstants.IMAGE_HEADERS,
                timeout=SauceConstants.IMAGE_TIMEOUT,
            )
            response.raise_for_status()
            if len(response.content) > SauceConstants.IMAGE_MAXIMUM_SIZE:
                raise ImageSourceOversizedException
            return UploadFileIO(response.content)
        except HTTPError as e:
            raise UnavailableSourceException(detail=str(e)) from e

    @catch_network_error
    async def request(
        self, *, file: UploadFileIO, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = await self.client.post(
            url=self._join(
                self.base,
                "search.php",
                params={
                    **params,
                    "api_key": random.choice(SauceConstants.API_KEY),
                    "output_type": 2,
                },
            ),
            files={"file": file},
        )
        if response.status_code >= 500:
            response.raise_for_status()
        return response.json()

    @overload
    async def search(
        self,
        *,
        url: HostUrl,
        size: int = 30,
        deduplicate: DeduplicateType = DeduplicateType.ALL,
        database: Optional[int] = None,
        enabled_mask: Optional[int] = None,
        disabled_mask: Optional[int] = None,
    ) -> Dict[str, Any]:
        ...

    @overload
    async def search(
        self,
        *,
        file: UploadFileIO,
        size: int = 30,
        deduplicate: DeduplicateType = DeduplicateType.ALL,
        database: Optional[int] = None,
        enabled_mask: Optional[int] = None,
        disabled_mask: Optional[int] = None,
    ) -> Dict[str, Any]:
        ...

    async def search(
        self,
        *,
        url: Optional[HostUrl] = None,
        file: Optional[UploadFileIO] = None,
        size: int = 30,
        deduplicate: DeduplicateType = DeduplicateType.ALL,
        database: Optional[int] = None,
        enabled_mask: Optional[int] = None,
        disabled_mask: Optional[int] = None,
    ):
        if url is not None:
            file = await self.fetch(url)
        assert file is not None
        return await self.request(
            file=file,
            params={
                "dbmask": enabled_mask,
                "dbmaski": disabled_mask,
                "db": database,
                "numres": size,
                "dedupe": deduplicate,
            },
        )
