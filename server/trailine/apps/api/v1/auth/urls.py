from django.urls import path

from trailine.apps.api.v1.auth.views import auth_email_request


urlpatterns = [
    path("auth/email/request", auth_email_request, name="auth_email_request")
]
