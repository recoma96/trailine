from django.urls import path

from trailine.apps.api.v1.health.views import HealthCheckView

urlpatterns = [
    path("", HealthCheckView.as_view(), name="health_check"),
]
