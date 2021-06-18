import asyncio
from typing import NoReturn
from urllib.parse import ParseResult

import sentry_sdk
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.logging import LoggingIntegration

from hibiapi import __version__
from hibiapi.utils.config import Config
from hibiapi.utils.log import logger
from hibiapi.utils.temp import TempFile

from .routes import router as ImplRouter

DESCRIPTION = """
**An alternative implement of Imjad API**

- *Documents*:
    - [Redoc](/docs) (Easier to read and more beautiful)
    - [Swagger UI](/docs/test) (Integrated interactive testing function)

Project: [mixmoe/HibiAPI](https://github.com/mixmoe/HibiAPI)

![](https://img.shields.io/github/stars/mixmoe/HibiAPI?color=brightgreen&logo=github&style=for-the-badge)
"""

if slogan := Config["content"]["slogan"].as_str().strip():
    DESCRIPTION += "\n" + slogan


if Config["log"]["sentry"]["enabled"].as_bool():
    sentry_sdk.init(
        dsn=Config["log"]["sentry"]["dsn"].as_str(),
        send_default_pii=Config["log"]["sentry"]["pii"].as_bool(),
        integrations=[LoggingIntegration(level=None, event_level=None)],
        traces_sample_rate=Config["log"]["sentry"]["sample"].get(float),
    )


app = FastAPI(
    debug=Config["debug"].as_bool(),
    title="HibiAPI",
    version=__version__,
    description=DESCRIPTION,
    docs_url="/docs/test",
    redoc_url="/docs",
)
app.include_router(ImplRouter, prefix="/api")
app.mount(
    "/temp",
    StaticFiles(directory=str(TempFile.path), check_dir=False),
    "Temporary file directory",
)


@app.get("/", include_in_schema=False)
async def redirect():
    return Response(status_code=302, headers={"Location": "/docs"})


@app.get("/robots.txt", include_in_schema=False)
async def robots():
    content = Config["content"]["robots"].as_str().strip()
    return Response(content, status_code=200)


@app.on_event("startup")
async def cleaner():
    async def clean() -> NoReturn:
        while True:
            try:
                await TempFile.clean()
            except Exception:
                logger.exception("Exception occurred during executing cleaning task:")
            await asyncio.sleep(3600)

    asyncio.ensure_future(clean())


@app.on_event("shutdown")
def flush_sentry():
    client = sentry_sdk.Hub.current.client
    if client is not None:
        client.close()
    sentry_sdk.flush()
    logger.info("Sentry client has been closed")


"""
Temporary redirection solution below for #12
"""


def _redirect(request: Request, path: str, to: str) -> Response:
    return Response(
        status_code=301,
        headers={
            "Location": ParseResult(
                scheme="",
                netloc="",
                path=path + to,
                params="",
                query=str(request.query_params),
                fragment="",
            )
        },
    )


@app.get("/qrcode/{path:path}", include_in_schema=False)
async def _qr_redirect(path: str, request: Request):
    return _redirect(request, path, "/api/qrcode/")


@app.get("/pixiv/{path:path}", include_in_schema=False)
async def _pixiv_redirect(path: str, request: Request):
    return _redirect(request, path, "/api/pixiv/")


@app.get("/netease/{path:path}", include_in_schema=False)
async def _netease_redirect(path: str, request: Request):
    return _redirect(request, path, "/api/netease/")


@app.get("/bilibili/{path:path}", include_in_schema=False)
async def _bilibili_redirect(path: str, request: Request):
    return _redirect(request, path, "/api/bilibili/")
