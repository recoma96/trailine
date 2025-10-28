from rest_framework import serializers

from trailine.apps.users.models import User


class _BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class CreateUserSerializer(_BaseUserSerializer):

    class Meta(_BaseUserSerializer.Meta):
        fields = (
            "id",
            "nickname",
            "email",
            "password",
            "gender",
            "birthday",
            # "profile_image_url" 추후 추가 개발 예정
        )


class CreateUserResponseSerializer(serializers.Serializer):
    """
    Swagger 노출용 Serializer
    실제로는 사용하지 않음
    """
    access = serializers.CharField(help_text="엑세스 토큰")
    refresh = serializers.CharField(help_text="리프레시 토큰")
