from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from trailine.apps.api.v1.auth.views import auth_email_request, verify_email
from trailine.apps.api.v1.users.views import logout_view

urlpatterns = [
    path("auth/email/request", auth_email_request, name="auth_email_request"),
    path("auth/email/verify", verify_email, name="verify_email"),

    path("auth/login", TokenObtainPairView.as_view(), name="token_login"),
    path("auth/logout", logout_view, name="token_logout"),
    path("auth/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
