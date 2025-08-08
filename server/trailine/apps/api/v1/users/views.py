from typing import Dict, Any

from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from trailine.apps.api.v1.auth.types import AuthRequestPurpose
from trailine.apps.api.v1.users.serializers import (
    CreateUserSerializer,
    CreateUserResponseSerializer
)
from trailine.apps.common.exc import NeedEmailAuth
from trailine.apps.common.utils import get_verify_success_email_cache_key
from trailine.apps.users.models import User


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin
):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    tokens: Dict[str, str]      # 회원가입 이후 토큰 발급을 위해 추가된 변수

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.tokens = {}

    def get_serializer_class(self):
        return {
            "create": CreateUserSerializer
        }.get(self.action, self.serializer_class)

    @swagger_auto_schema(
        operation_summary="회원가입",
        responses={
            status.HTTP_201_CREATED: CreateUserResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: "이메일 인증이 완료되지 않음",
            status.HTTP_400_BAD_REQUEST: "사용자 입력에 대한 실패",
        }
    )
    def create(self, request, *args, **kwargs):

        # 이메일 인증 여부 확인
        email = request.data.get("email", "")
        verify_success_email_key = get_verify_success_email_cache_key(email, AuthRequestPurpose.SIGNUP.value)
        if not cache.get(verify_success_email_key):
            raise NeedEmailAuth

        super().create(request, *args, **kwargs)

        return Response(
            data=self.tokens,
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer: CreateUserSerializer):
        # 유저 생성
        new_user = serializer.save()

        # 생성 이후 토큰 발급
        refresh = RefreshToken.for_user(new_user)
        self.tokens: Dict[str, str] = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        # 이메일 인증 캐싱 데이터 소멸
        verify_success_email_key = get_verify_success_email_cache_key(new_user.email, AuthRequestPurpose.SIGNUP.value)
        cache.delete(verify_success_email_key)

