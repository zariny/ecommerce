from django.test import TestCase
from account.views import SetAuthenticationCookiesMixin
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.utils import timezone
from datetime import datetime


User = get_user_model()


class TestSetAuthenticationCookiesMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User._default_manager.create_user(email="example@email.com", password="strong-password")

    def setUp(self):
        self.auth_cookies = ["access_token", "refresh_token", "expiry_date"]
        self.response_obj = Response()
        self.mixin = SetAuthenticationCookiesMixin()

    def test_auth_cookies_were_set_correctly(self):
        refresh_token = RefreshToken.for_user(self.user)
        self.mixin.set_auth_tokens(self.response_obj, refresh_token)
        cookies = self.response_obj.cookies

        for cookie_name in self.auth_cookies:
            self.assertIn(cookie_name, cookies)
            self.assertTrue(cookies[cookie_name]["secure"])
            self.assertEqual(cookies[cookie_name]["samesite"], "None")

        self.assertEqual(cookies["refresh_token"].value, str(refresh_token))
        self.assertEqual(cookies["refresh_token"]["max-age"], refresh_token.lifetime.total_seconds())
        self.assertEqual(cookies["expiry_date"]["max-age"], refresh_token.lifetime.total_seconds())
        self.assertTrue(cookies["refresh_token"]["httponly"])
        self.assertTrue(cookies["access_token"]["httponly"])
        self.assertFalse(cookies["expiry_date"]["httponly"])

        access_token = AccessToken(cookies["access_token"].value)
        self.assertEqual(access_token["user_id"], self.user.id)
        x = timezone.localtime(
            timezone.make_aware(datetime.fromtimestamp(access_token["exp"]))
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        self.assertEqual(x, cookies["expiry_date"].value)
