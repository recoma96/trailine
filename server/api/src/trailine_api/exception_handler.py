from fastapi import Request
from fastapi.responses import JSONResponse

from trailine_api.common.exc import TrailineException


async def trailine_exception_handler(request: Request, exc: TrailineException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "errorCode": exc.error_code,
            "message": exc.error_message,
        },
    )
