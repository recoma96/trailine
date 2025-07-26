from unittest.mock import patch

from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase


class VerifyEmailTests(APITestCase):
    @patch("trailine.apps.api.v1.auth.services.cache.set")
    @patch("trailine.apps.api.v1.auth.services.cache.delete")
    @patch("trailine.apps.api.v1.auth.services.cache.get", return_value="ABC123")
    @patch("trailine.apps.api.v1.auth.services.verify_email_code")
    def test_verify_email_success(self, mock_verify_email_code, mock_cache_get, mock_cache_delete, mock_cache_set):
        url = reverse("verify_email")
        data = {
            "email": "testuser@example.com",
            "purpose": "signup",
            "code": "ABC123"
        }

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_cache_set.assert_called_with(
            "verify:email:signup:dGVzdHVzZXJAZXhhbXBsZS5jb20=:success",
            1,
            timeout=settings.EMAIL_VERIFICATION_SUCCESS_TIMEOUT
        )

    @patch("trailine.apps.api.v1.auth.views.verify_email_code", side_effect=Exception("Invalid code"))
    def test_verify_email_code_failure(self, mock_verify_email_code):
        url = reverse("verify_email")
        data = {
            "email": "testuser@example.com",
            "purpose": "signup",
            "code": "INVALID"
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
