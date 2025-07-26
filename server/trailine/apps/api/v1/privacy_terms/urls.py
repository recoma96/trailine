from django.urls import include, path
from rest_framework.routers import DefaultRouter

from trailine.apps.api.v1.privacy_terms.views import PrivacyTermViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"privacy-terms", PrivacyTermViewSet)

urlpatterns = router.urls
