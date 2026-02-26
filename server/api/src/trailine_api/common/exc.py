from fastapi import status


class TrailineException(Exception):
    status_code: int
    error_code: str
    error_message: str


class ApiNotImplemented(TrailineException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    error_code = "NOT-IMPLEMENTED"
    error_message = "준비중이에요"


class MountainAreaNotFound(TrailineException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "MOUNTAIN-AREA-NOT-FOUND"
    error_message = "주변 산악 지형을 찾을수 없어요"
