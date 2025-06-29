from django.urls import path

from trailine.apps.api.v1.auth.views import auth_email_request, verify_email

urlpatterns = [
    path("auth/email/request", auth_email_request, name="auth_email_request"),
    path("auth/email/verify", verify_email, name="verify_email")
]
