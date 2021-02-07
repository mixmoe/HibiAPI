from io import BytesIO
from typing import Optional

from api.sauce import (
    DeduplicateType,
    HostUrl,
    NetRequest,
    SauceConstants,
    SauceEndpoint,
)
from fastapi import Depends, File, Form
from utils.utils import SlashRouter

router = SlashRouter(tags=["SauceNAO"])

SauceAPIRoot = NetRequest()


async def requestClient():
    async with SauceAPIRoot as client:
        yield SauceEndpoint(client)


@router.get("/")
async def sauce_url(
    url: HostUrl,
    size: int = 30,
    deduplicate: DeduplicateType = DeduplicateType.ALL,
    database: Optional[int] = None,
    enabled_mask: Optional[int] = None,
    disabled_mask: Optional[int] = None,
    endpoint: SauceEndpoint = Depends(requestClient),
):
    return await endpoint.search(
        url=url,
        size=size,
        deduplicate=deduplicate,
        database=database,
        enabled_mask=enabled_mask,
        disabled_mask=disabled_mask,
    )


@router.post("/")
async def sauce_form(
    file: bytes = File(..., max_length=SauceConstants.IMAGE_MAXIMUM_SIZE),
    size: int = Form(30),
    deduplicate: DeduplicateType = Form(DeduplicateType.ALL),
    database: Optional[int] = Form(None),
    enabled_mask: Optional[int] = Form(None),
    disabled_mask: Optional[int] = Form(None),
    endpoint: SauceEndpoint = Depends(requestClient),
):
    return await endpoint.search(
        file=BytesIO(file),
        size=size,
        deduplicate=deduplicate,
        database=database,
        disabled_mask=disabled_mask,
        enabled_mask=enabled_mask,
    )
