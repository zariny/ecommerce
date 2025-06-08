from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from account.views import UserAuthenticationView


User = get_user_model()


class TestUserAuthenticationView(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = "example@email.com"
        cls.password = "example"
        cls.user = User._default_manager.create_user(email=cls.email, password=cls.password)
        cls.login_url = "/api/login/"
        cls.logout_url = cls.login_url

    def test_successful_login_returns_token_via_cookies(self):
        response = self.client.post(self.login_url, {"email": self.email, "password": self.password})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.email)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertIn("expiry_date", response.cookies)

    def test_invalid_password_returns_401(self):
        response = self.client.post(self.login_url, {"email": self.email, "password": "Invalid password"})
        self.assertEqual(response.status_code, 401)

    def test_deactivate_user_returns_403(self):
        pass

    def test_missing_field_returns_400(self):
        response = self.client.post(self.login_url, {"email": self.email})
        self.assertEqual(response.status_code, 400)

    def test_successful_logout_destroy_cookies(self):
        # First of all, login to receive authentication cookies.
        login_response = self.client.post(self.logout_url, {"email": self.email, "password": self.password})
        self.assertEqual(login_response.status_code, 200)
        self.client.cookies = login_response.cookies
        logout_response = self.client.delete(self.logout_url)
        self.assertEqual(logout_response.status_code, 200)
        self.assertEqual(logout_response.cookies["access_token"].value, "")
        self.assertEqual(logout_response.cookies["refresh_token"].value, "")
        self.assertEqual(logout_response.cookies["expiry_date"].value, "")

    def test_logout_without_cookies_returns_200(self):
        self.client.cookies = {}
        reponse = self.client.delete(self.logout_url)
        self.assertEqual(reponse.status_code, 200)
