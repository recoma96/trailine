from django.urls import path, include


urlpatterns = [
    path("health", include("trailine.apps.api.v1.health.urls")),
    path("", include("trailine.apps.api.v1.privacy_terms.urls"))
]
