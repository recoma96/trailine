from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from trailine.apps.api.v1.auth.types import AuthRequestPurpose
from trailine.apps.common.utils import get_verify_success_email_cache_key
from trailine.tests.conftest import PrivacyTermFactory, PrivacyTermVersionFactory


class CreateUserTestCase(APITestCase):
    # url(user-list)를 사용하는 이유는 GET, POST가 viewset에 의해 user-list에 포함되기 때문이다.
    required_privacy_term: PrivacyTermVersionFactory

    @classmethod
    def setUp(cls):
        _required_privacy_term_base = PrivacyTermFactory.create()
        cls.required_privacy_term = PrivacyTermVersionFactory.create(
            privacy_term=_required_privacy_term_base, is_required=True)

    @patch("trailine.apps.api.v1.users.views.cache.get", return_value=None)
    def test_create_user_email_not_verified(self, mock_cache_get):
        url = reverse("user-list")
        data = {
            "email": "testuser@example.com",
            "nickname": "failed",
            "password": "TestPassword123",
            "termAgreements": [
                {
                    "termId": self.required_privacy_term.privacy_term.id,
                    "isAgree": True
                }
            ]
        }
        response = self.client.post(url, data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_cache_get.assert_called_once_with(
            get_verify_success_email_cache_key("testuser@example.com", AuthRequestPurpose.SIGNUP.value)
        )

    @patch("trailine.apps.api.v1.users.views.cache.get", return_value=True)
    def test_create_user_success(self, mock_cache_get):
        url = reverse("user-list")
        data = {
            "email": "testuser@example.com",
            "nickname": "success",
            "password": "TestPassword123",
            "termAgreements": [
                {
                    "termId": self.required_privacy_term.privacy_term.id,
                    "isAgree": True
                }
            ]
        }
        response = self.client.post(url, data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_cache_get.assert_called_once_with(
            get_verify_success_email_cache_key("testuser@example.com", AuthRequestPurpose.SIGNUP.value)
        )

    @patch("trailine.apps.api.v1.users.views.cache.get", return_value=True)
    def test_create_user_empty_term_agreements(self, mock_cache_get):
        url = reverse("user-list")
        data = {
            "email": "testuser@example.com",
            "nickname": "failed",
            "password": "TestPassword123",
            "termAgreements": []
        }
        response = self.client.post(url, data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_cache_get.assert_called_once_with(
            get_verify_success_email_cache_key("testuser@example.com", AuthRequestPurpose.SIGNUP.value)
        )

    @patch("trailine.apps.api.v1.users.views.cache.get", return_value=True)
    def test_create_user_required_term_disagree(self, mock_cache_get):
        url = reverse("user-list")
        data = {
            "email": "testuser@example.com",
            "nickname": "failed",
            "password": "TestPassword123",
            "termAgreements": [
                {
                    "termId": self.required_privacy_term.privacy_term.id,
                    "isAgree": False
                }
            ]
        }
        response = self.client.post(url, data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_cache_get.assert_called_once_with(
            get_verify_success_email_cache_key("testuser@example.com", AuthRequestPurpose.SIGNUP.value)
        )
