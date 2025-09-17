from unittest.mock import patch, MagicMock
from django.db.models.expressions import result
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from utils.authenticate import JWTCookiesBaseAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class TestJWTCookiesBaseAuthentication(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.auth = JWTCookiesBaseAuthentication()

    def test_no_cookies_returns_none(self):
        request = self.factory.get("/")
        request.COOKIES = {}
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    @patch.object(JWTCookiesBaseAuthentication, attribute="get_validated_token")
    def test_invalid_token_returns_none(self, mock_get_validated_token):
        request = self.factory.get("/")
        request.COOKIES = {"access_token": "Invalid Token!"}
        mock_get_validated_token.side_effect = InvalidToken("Invalid token.")
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    @patch.object(JWTCookiesBaseAuthentication, attribute="get_validated_token")
    @patch.object(JWTCookiesBaseAuthentication, attribute="get_user")
    def test_valid_token_but_no_user_returns_none(self, mock_get_user, mock_get_validated_token):
        request = self.factory.get("/")
        request.COOKIES = {"access_token": "Valid Token"}
        mock_get_user.return_value = None
        mock_get_validated_token.return_value = MagicMock()
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    @patch.object(JWTCookiesBaseAuthentication, attribute="get_validated_token")
    @patch.object(JWTCookiesBaseAuthentication, attribute="get_user")
    def test_valid_token_and_user_returns_tuple(self, mock_get_user, mock_get_validated_token):
        request = self.factory.get("/")
        request.COOKIES = {"access_token": "Valid Token"}
        mock_user = MagicMock()
        mock_token = MagicMock()
        mock_get_user.return_value = mock_user
        mock_get_validated_token.return_value = mock_token
        result = self.auth.authenticate(request)
        self.assertEqual(result, (mock_user, mock_token))
