from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("trailine.apps.api.v1.urls")),
    path("api/v2/", include("trailine.apps.api.v2.urls")),
]
