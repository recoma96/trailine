from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("trailine.apps.api.v1.urls")),
    path("api/v2/", include("trailine.apps.api.v2.urls")),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="Trailine API Document",
            default_version="v1",
            description="Trailine 서버 API 문서야",
            contact=openapi.Contact(email="seokbong60@gmail.com"),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )

    urlpatterns += [
        re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
        path("swagger", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),

        # ReDoc
        path("redoc", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ]
