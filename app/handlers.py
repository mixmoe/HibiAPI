from fastapi import Request

#
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError as FastAPIValidationError
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from utils.exceptions import (
    BaseHTTPException,
    BaseServerException,
    ClientSideException,
    ExceptionStorage,
    UncaughtException,
    ValidationException,
)
from utils.log import logger

from .application import app


@app.exception_handler(BaseServerException)
async def exceptionHandler(request: Request, exc: BaseServerException) -> JSONResponse:
    exc.data.url = str(request.url)  # type:ignore
    try:
        raise exc
    except UncaughtException as e:
        exc.data.trace = ExceptionStorage.save(e.exc.__traceback__)
    except BaseServerException:
        pass
    if exc.data.code >= 500:
        logger.opt(exception=exc).exception(
            f"Error occurred during parsing <r><b>({exc.data=})</b></r>:"
        )
    return JSONResponse(
        content=exc.data.dict(exclude_none=True, exclude_defaults=True),
        headers=exc.data.headers,
        status_code=exc.data.code,
    )


@app.exception_handler(StarletteHTTPException)
async def overrideHandler(request: Request, exc: StarletteHTTPException):
    return await exceptionHandler(
        request,
        BaseHTTPException(
            exc.detail,
            code=exc.status_code,
            headers={} if not isinstance(exc, FastAPIHTTPException) else exc.headers,
        ),
    )


@app.exception_handler(AssertionError)
async def assertionHandler(request: Request, exc: AssertionError):
    return await exceptionHandler(
        request, ClientSideException(detail=f"Assertion: {exc}")
    )


@app.exception_handler(FastAPIValidationError)
@app.exception_handler(PydanticValidationError)
async def validationHandler(request: Request, exc: PydanticValidationError):
    return await exceptionHandler(
        request, ValidationException(detail=str(exc), validation=exc.errors())
    )
