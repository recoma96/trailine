from rest_framework.routers import DefaultRouter

from trailine.apps.api.v1.users.views import UserViewSet

router = DefaultRouter(trailing_slash=False)

router.register(r"users", UserViewSet)

urlpatterns = router.urls
