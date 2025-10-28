from django.urls import path, include


urlpatterns = [
    path("health", include("trailine.apps.api.v1.health.urls")),
    path("", include("trailine.apps.api.v1.auth.urls")),
    path("", include("trailine.apps.api.v1.users.urls")),
]
