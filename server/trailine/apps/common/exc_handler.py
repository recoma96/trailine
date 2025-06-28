from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rest_framework.views import exception_handler as pre_exception_handler


def exception_handler(exc: Exception, context):
    response = pre_exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={
                "errorCode": "VALIDATION-FAILED",
                "errorMessage": "파라미터 형식이 잘못되었어요.",
                "extraData": exc.args
            }
        )

    return response
