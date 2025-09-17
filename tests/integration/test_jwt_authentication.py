from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIRequestFactory
from utils.authenticate import JWTCookiesBaseAuthentication


class TestJWTCookiesBaseAuthentication(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User._default_manager.create(email="example@email.com", password="example")
        cls.factory = APIRequestFactory()
        cls.auth = JWTCookiesBaseAuthentication()

    def test_valid_user_with_valid_token(self):
        request = self.factory.get("/")
        token = self.generate_token_for_user()
        request.COOKIES = {"access_token": token}
        result = self.auth.authenticate(request)
        user, token_data = result
        self.assertEqual(user, self.user)
        self.assertEqual(str(token_data), token)

    def generate_token_for_user(self):
        refresh_token = RefreshToken.for_user(self.user)
        return str(refresh_token.access_token)
