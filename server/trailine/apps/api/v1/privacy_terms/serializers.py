from rest_framework import serializers

from trailine.apps.privacy_terms.models import PrivacyTermVersion, PrivacyTerm


class PrivacyTermVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyTermVersion
        exclude = ["privacy_term"]


class PrivacyTermSerializer(serializers.ModelSerializer):
    versions = PrivacyTermVersionSerializer(many=True, read_only=True)

    class Meta:
        model = PrivacyTerm
        fields = "__all__"


class LatestPrivacyTermSerializer(serializers.ModelSerializer):
    term_id = serializers.CharField(source="id", read_only=True, help_text="약관 고유 아이디")
    term_code = serializers.CharField(source="code", read_only=True, help_text="약관 고유 코드")
    term_name = serializers.CharField(source="name", read_only=True, help_text="약관 이름")

    version_id = serializers.IntegerField(read_only=True, help_text="약관 버전 고유 아이디")
    version_value = serializers.IntegerField(read_only=True, help_text="약관 버전 값")
    title = serializers.CharField(read_only=True, help_text="약관 제목")
    content = serializers.CharField(read_only=True, help_text="약관 내용")
    is_required = serializers.BooleanField(read_only=True, help_text="필수 어부")
    version_created_at = serializers.DateTimeField(read_only=True, help_text="약관 버전 생성 날짜")

    class Meta:
        model = PrivacyTerm
        fields = (
            "term_id",
            "term_code",
            "term_name",
            "version_id",
            "version_value",
            "title",
            "content",
            "is_required",
            "version_created_at"
        )
