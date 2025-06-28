from rest_framework.exceptions import APIException
from typing import Any, Optional


class TrailineAPiException(APIException):
    def __init__(
        self,
        http_status: int,
        error_code: str,
        message: str,
        extra_data: Optional[Any] = None
    ):
        self.http_status = http_status
        self.error_code = error_code
        self.message = message
        self.extra_data = extra_data
        self.status_code = http_status
        super().__init__(detail=self.get_response_data())

    def get_response_data(self) -> dict:
        response_data = {
            "errorCode": self.error_code,
            "errorMessage": self.message,
            "extraData": self.extra_data
        }
        return response_data
