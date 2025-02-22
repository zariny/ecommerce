from typing import Optional, Tuple
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication, AuthUser
from rest_framework_simplejwt.tokens import Token
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class JWTCookiesBaseAuthentication(JWTAuthentication):
    def authenticate(self, request: Request) -> Optional[Tuple[AuthUser, Token]]:
        token = request.COOKIES.get("access_token")
        if token is None:
            return
        try:
            validated_token = self.get_validated_token(token)
        except InvalidToken:
            return None

        user = self.get_user(validated_token)
        if user is None:
            return None

        return (user, validated_token)


class JWTCookiesAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = JWTCookiesBaseAuthentication
    name = "JWT Cookies Auth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "",
            "bearerFormat": "JWT"
        }
