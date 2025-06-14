from django.db.models import OuterRef, Subquery, QuerySet

from trailine.apps.privacy_terms.models import PrivacyTerm, PrivacyTermVersion


class PrivacyTermService:
    @staticmethod
    def get_latest_privacy_terms() -> QuerySet:
        """
        최신 버전의 약관 항목들만 가져오는 쿼리를 리턴하는 함수
        """

        """
        Raw Query Version
        
        SELECT
            pt.id AS privacy_term_id,
            pt.code AS privacy_term_code,
            pt.name AS privacy_term_name,
            ptv.id AS privacy_term_version_id,
            ptv.version AS privacy_term_version_value,
            ptv.title AS privacy_term_title,
            ptv.content AS privacy_term_content,
            ptv.created_at AS privacy_term_created_at
        FROM privacy_term_version ptv
        JOIN (
            SELECT privacy_term_id, MAX(version) AS max_version
            FROM privacy_term_version
            GROUP BY privacy_term_id
        ) latest
            ON ptv.privacy_term_id = latest.privacy_term_id
            AND ptv.version = latest.max_version
        JOIN privacy_terms pt ON ptv.privacy_term_id = pt.id;
        """

        # Sub Query: version이 큰 순서대로 정렬
        latest_versions = PrivacyTermVersion.objects.filter(
            privacy_term_id=OuterRef("id")
        ).order_by("-version")

        # [:1] -> LIMIT 1
        terms = PrivacyTerm.objects.annotate(
            version_id=Subquery(latest_versions.values("id")[:1]),
            version_value=Subquery(latest_versions.values("version")[:1]),
            title=Subquery(latest_versions.values("title")[:1]),
            content=Subquery(latest_versions.values("content")[:1]),
            version_created_at=Subquery(latest_versions.values("created_at")[:1]),
            is_required=Subquery(latest_versions.values("is_required")[:1]),
        )

        return terms
