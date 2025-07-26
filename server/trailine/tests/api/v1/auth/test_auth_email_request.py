from unittest.mock import patch

from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase


class AuthEmailRequestTests(APITestCase):
    @patch("trailine.apps.api.v1.auth.services.cache.set")
    @patch("trailine.apps.api.v1.auth.services.send_mail", return_value=1)
    @patch("trailine.apps.api.v1.auth.services.generate_verification_code", return_value="ABC123")
    def test_auth_email_request_success(self, mock_generate_code, mock_send_mail, mock_cache_set):
        url = reverse("auth_email_request")
        data = {
            "email": "testuser@example.com",
            "purpose": "signup"
        }

        response = self.client.post(url, data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 캐시에 아래와 같은 값이 제대로 저장되어 있는 지 확인
        mock_cache_set.assert_called_with(
            "verify:email:signup:dGVzdHVzZXJAZXhhbXBsZS5jb20=",
            "ABC123",
            timeout=settings.EMAIL_VERIFICATION_TIMEOUT
        )

    def test_auth_email_request_invalid_purpose(self):
        url = reverse("auth_email_request")
        data = {
            "email": "testuser@example.com",
            "purpose": "invalid-purpose"
        }

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("trailine.apps.api.v1.auth.services.send_mail", return_value=0)
    @patch("trailine.apps.api.v1.auth.utils.generate_verification_code", return_value="ABC123")
    def test_auth_email_request_send_mail_failure(self, mock_generate_code, mock_send_mail):
        url = reverse("auth_email_request")
        data = {
            "email": "testuser@example.com",
            "purpose": "signup"
        }

        response = self.client.post(url, data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 이메일 송신을 딱 한번만 했는지 확인 (중복 발송이 일어나서는 안된다)
        mock_send_mail.assert_called_once()
