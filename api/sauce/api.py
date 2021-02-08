from enum import IntEnum
from io import BytesIO
from typing import Any, Dict, Optional, overload

from httpx import HTTPError
from utils.exceptions import ClientSideException
from utils.net import catch_network_error
from utils.routing import BaseEndpoint, BaseHostUrl

from .constants import SauceConstants


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


class DeduplicateType(IntEnum):
    """
    0=no result deduping
    1=consolidate booru results and dedupe by item identifier
    2=all implemented dedupe methods such as by series name.
    Default is 2, more levels may be added in future.
    """

    DISABLED = 0
    IDENTIFIER = 1
    ALL = 2


class SauceEndpoint(BaseEndpoint):
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
        params.update({"api_key": SauceConstants.API_KEY, "output_type": 2})
        response = await self.client.post(
            url=self._join(self.base, "search.php", params), files={"file": file}
        )
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
    ):
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
    ):
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
