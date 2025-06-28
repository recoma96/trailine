from rest_framework import serializers

from trailine.apps.api.v1.auth.types import AuthRequestPurpose
from trailine.apps.common.enums import AuthRequestPurposeEnum


class AuthEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True, help_text="이메일")
    purpose = serializers.ChoiceField(choices=AuthRequestPurpose.choices(), required=True, help_text="인증목적")

    def validate_purpose(self, value):
        if value not in [purpose.value for purpose in AuthRequestPurposeEnum]:
            raise serializers.ValidationError("해당 목적으로 요청을 할 수가 없어요")
        return value
