from fastapi import Request, Response
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError as FastAPIValidationError
from pydantic.error_wrappers import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from hibiapi.utils import exceptions
from hibiapi.utils.log import logger

from .application import app


@app.exception_handler(exceptions.BaseServerException)
async def exception_handler(
    request: Request,
    exc: exceptions.BaseServerException,
) -> Response:
    if isinstance(exc, exceptions.UncaughtException):
        exc.data.trace = (
            exceptions.ExceptionInfo.new(exc.exc.__traceback__).persist().id
        )
    exc.data.url = str(request.url)  # type:ignore
    if exc.data.code >= 500:
        logger.opt(exception=exc).exception(
            f"Error occurred during parsing {exc.data}:"
        )
    return Response(
        content=exc.data.json(),
        status_code=exc.data.code,
        headers=exc.data.headers,
        media_type="application/json",
    )


@app.exception_handler(StarletteHTTPException)
async def override_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    return await exception_handler(
        request,
        exceptions.BaseHTTPException(
            exc.detail,
            code=exc.status_code,
            headers={} if not isinstance(exc, FastAPIHTTPException) else exc.headers,
        ),
    )


@app.exception_handler(AssertionError)
async def assertion_handler(request: Request, exc: AssertionError):
    return await exception_handler(
        request,
        exceptions.ClientSideException(detail=f"Assertion: {exc}"),
    )


@app.exception_handler(FastAPIValidationError)
@app.exception_handler(PydanticValidationError)
async def validation_handler(request: Request, exc: PydanticValidationError):
    return await exception_handler(
        request,
        exceptions.ValidationException(detail=str(exc), validation=exc.errors()),
    )
