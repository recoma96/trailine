from rest_framework.exceptions import APIException
from rest_framework import status

from typing import Any, Dict, List


class TrailineAPIException(APIException):
    """Trailine API의 기본 예외 클래스"""

    # 기본값 설정
    status_code: int
    error_code: str
    message: str
    extra_data: List | Dict[str, Any] | str | None

    def __init__(
            self,
            http_status: int | None = None,
            error_code: str | None = None,
            message: str | None = None,
            extra_data: List | Dict[str, Any] | str | None = None
    ):
        self.extra_data = None

        self.status_code = http_status or self.status_code
        self.error_code = error_code or self.error_code
        self.message = message or self.message
        self.extra_data = extra_data or self.extra_data

        super().__init__(detail=self.get_response_data())

    def get_response_data(self) -> dict[str, Any]:
        response = {
            "errorCode": self.error_code,
            "errorMessage": self.message
        }
        if self.extra_data:
            response["extraData"] = self.extra_data

        return response


class EmailSendFailed(TrailineAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "EMAIL-SEND-FAILED"
    message = "이메일 전송에 실패했어요."


class EmailSendNotAccepted(TrailineAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "EMAIL-SEND-NOT-ACCEPTED"
    message = "이메일 송신이 거부되었어요."


class AuthCodeNotExist(TrailineAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "AUTH-CODE-NOT-EXIST"
    message = "이메일 인증을 요청하지 않았거나. 인증 시간이 만료가 되었어요. 다시 시도해 주세요."


class AuthCodeNotMatched(TrailineAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "AUTH-CODE-NOT-MATCHED"
    message = "인증번호가 틀렸어요. 다시 입력해 주세요."
