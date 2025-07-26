from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request

from trailine.apps.api.v1.privacy_terms.serializers import (
    PrivacyTermSerializer,
    LatestPrivacyTermSerializer
)
from trailine.apps.api.v1.privacy_terms.services import PrivacyTermService
from trailine.apps.privacy_terms.models import PrivacyTerm


class PrivacyTermViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PrivacyTerm.objects.prefetch_related("versions")
    serializer_class = PrivacyTermSerializer

    @action(methods=["GET"], url_path="latest", detail=False, serializer_class=LatestPrivacyTermSerializer)
    def get_latest(self, request: Request):
        """
        - 최산 약관 가져오기

        <div>
        """
        terms = PrivacyTermService.get_latest_privacy_terms()

        # 페이지네이션 적용
        page = self.paginate_queryset(terms)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
