from typing import List, Dict, Any

from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ListSerializer

from trailine.apps.api.v1.privacy_terms.services import PrivacyTermService
from trailine.apps.users.models import User, UserPrivacyTerm


class _BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class _CreateUserTermAgreementSerializer(serializers.Serializer):
    term_id = serializers.IntegerField(required=True, help_text="약관 항목 고유 아이디")
    is_agree = serializers.BooleanField(required=True, help_text="약관 동의 여부")


class CreateUserSerializer(_BaseUserSerializer):
    term_agreements = ListSerializer(child=_CreateUserTermAgreementSerializer(), write_only=True)

    class Meta(_BaseUserSerializer.Meta):
        fields = (
            "id",
            "nickname",
            "email",
            "password",
            "gender",
            "birthday",
            # "profile_image_url" 추후 추가 개발 예정
            "term_agreements",
        )

    def validate_term_agreements(self, values: List[Dict[str, int | bool]]) -> List[Dict[str, int | bool]]:
        term_services = PrivacyTermService()
        terms = term_services.get_latest_privacy_terms()

        latest_version_terms = {term.version_id: term for term in terms}
        requested_terms = {value["term_id"]: value["is_agree"] for value in values}

        if latest_version_terms.keys() != requested_terms.keys():
            raise serializers.ValidationError("일부 약관이 빠져있거나 최신 약관에 대해 동의를 해야 해요.")

        for term_id, term in latest_version_terms.items():
            if term.is_required and not requested_terms[term_id]:
                raise serializers.ValidationError(f"'{term.name}' 항목에 대해 동의가 필요해요.")

        return values

    def create(self, validated_data):
        term_agreements = validated_data.pop("term_agreements")

        with transaction.atomic():
            new_user = User.objects.create_user(**validated_data)

            for term_agreement in term_agreements:
                term_id = term_agreement["term_id"]
                is_agree = term_agreement["is_agree"]

                agreed_at = new_user.created_at if is_agree else None
                UserPrivacyTerm.objects.create(
                    user=new_user,
                    privacy_term_version_id=term_id,
                    is_agreed=is_agree,
                    agreed_at=agreed_at,
                )

        return new_user


class CreateUserResponseSerializer(serializers.Serializer):
    """
    Swagger 노출용 Serializer
    실제로는 사용하지 않음
    """
    access = serializers.CharField(help_text="엑세스 토큰")
    refresh = serializers.CharField(help_text="리프레시 토큰")
