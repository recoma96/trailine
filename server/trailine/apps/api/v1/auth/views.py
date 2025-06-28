from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from trailine.apps.api.v1.auth.serializers import AuthEmailRequestSerializer
from trailine.apps.api.v1.auth.services import send_verify_email


@swagger_auto_schema(
    method="POST",
    operation_summary="이메일 인증 요청",
    request_body=AuthEmailRequestSerializer,
    responses={
        status.HTTP_204_NO_CONTENT: "요청 성공",
        status.HTTP_400_BAD_REQUEST: "입력 오류",
    }
)
@api_view(["POST"])
def auth_email_request(request: Request) -> Response:
    serializer = AuthEmailRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    purpose = serializer.validated_data["purpose"]
    send_verify_email(purpose, email)

    return Response(status=status.HTTP_204_NO_CONTENT)
