from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken

from trailine.apps.api.v1.auth.serializers import AuthEmailRequestSerializer, AuthEmailVerifySerializer
from trailine.apps.api.v1.auth.services import send_verify_email, verify_email_code


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


@swagger_auto_schema(
    method="POST",
    operation_summary="이메일 인증 확인",
    request_body=AuthEmailVerifySerializer,
    responses={
        status.HTTP_204_NO_CONTENT: "인증 성공",
        status.HTTP_400_BAD_REQUEST: "입력 오류, 혹은 인증 코드를 틀렸거나 만료됨",
    }
)
@api_view(["POST"])
def verify_email(request: Request) -> Response:
    serializer = AuthEmailVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    purpose = serializer.validated_data["purpose"]
    code = serializer.validated_data["code"]

    verify_email_code(purpose, email, code)
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='post',
    operation_description="Refresh 토큰을 블랙리스트 처리하여 JWT 로그아웃을 수행",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["refresh"],
        properties={
            "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh 토큰"),
        },
    ),
    responses={
        205: openapi.Response(description="로그아웃 성공"),
        400: openapi.Response(description="요청 오류 또는 유효하지 않은 토큰"),
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request: Request):
    refresh = request.data.get("refresh", "")
    if not refresh:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        RefreshToken(refresh).blacklist()
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_205_RESET_CONTENT)