from rest_framework.test import APITestCase
from account.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class TestTokenRefreshView(APITestCase):
    def setUp(self):
        self.refresh_url = "/api/refresh/"

    @classmethod
    def setUpTestData(cls):
        cls.user = User._default_manager.create_user(email="example@email.com", password="strong-password")

    def test_missing_token_returns_401(self):
        self.client.cookies = {}
        response = self.client.head(self.refresh_url)
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_returns_401(self):
        self.client.cookies["refresh_token"] = "invalid refresh token !"
        responses = self.client.head(self.refresh_url)
        self.assertEqual(responses.status_code, 401)

    def test_valid_token_returns_200(self):
        valid_token = RefreshToken.for_user(self.user)
        self.client.cookies["refresh_token"] =  valid_token
        responses = self.client.head(self.refresh_url)
        self.assertEqual(responses.status_code, 200)
        self.assertIn("access_token", responses.cookies)
        self.assertIn("expiry_date", responses.cookies)
