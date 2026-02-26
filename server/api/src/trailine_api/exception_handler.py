from fastapi import Request
from fastapi.responses import JSONResponse

from trailine_api.common.exc import TrailineException


async def trailine_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, TrailineException):
        return JSONResponse(
            status_code=500,
            content={
                "errorCode": "internal_error",
                "message": "Internal Server Error",
            },
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "errorCode": exc.error_code,
            "message": exc.error_message,
        },
    )
