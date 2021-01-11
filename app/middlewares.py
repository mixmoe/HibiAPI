import asyncio
from datetime import datetime
from typing import Any, Callable, Coroutine, List, NoReturn

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils.config import Config
from utils.exceptions import UncaughtException
from utils.log import logger
from utils.temp import TempFile

from .application import app
from .handlers import exceptionHandler

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config["server"]["cors"]["origins"].get(List[str]),
    allow_credentials=Config["server"]["cors"]["credentials"].as_bool(),
    allow_methods=Config["server"]["cors"]["methods"].get(List[str]),
    allow_headers=Config["server"]["cors"]["headers"].get(List[str]),
)
app.mount(
    "/temp",
    StaticFiles(directory=str(TempFile.path), check_dir=False),
    "Temporary file directory",
)


@app.middleware("http")
async def responseMiddleware(
    request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]
) -> Response:
    startTime = datetime.now()
    try:
        response = await call_next(request)
    except Exception as e:
        response = await exceptionHandler(
            request,
            UncaughtException.with_exception(e),
        )
    processTime = (datetime.now() - startTime).total_seconds() * 1000
    response.headers["X-Process-Time"] = f"{processTime:.3f}"
    logColor = (
        "green"
        if response.status_code < 400
        else "yellow"
        if response.status_code < 500
        else "red"
    )
    logger.info(
        "|".join(
            [
                f"<{logColor.upper()}><b>{request.method.upper()}</b></{logColor.upper()}>",  # noqa:E501
                f"<n><b>{str(request.url)!r}</b></n>",
                f"<c>{processTime:.3f}ms</c>",
                f"<e>{request.headers.get('user-agent','<d>Unknown</d>')}</e>",
                f"<b><{logColor}>{response.status_code}</{logColor}></b>",
            ]
        )
    )
    return response


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
