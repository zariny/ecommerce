from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from . import serializers


User = get_user_model()

class SetAuthenticationCookiesMixin:
    def set_auth_tokens(self, response, refresh_token):
        response.set_cookie(
            key="refresh_token",
            value=str(refresh_token),
            httponly=True,
            samesite="Lax",
            max_age=604800
        )
        access_token = refresh_token.access_token
        self.set_access_token(response, access_token)

    def set_access_token(self, response, access_token):
        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,
            samesite="Lax",
            max_age=300
        )
        response.set_cookie(
            key="expiry_date",
            value=access_token.current_time,
            httponly=False,
            samesite="Lax",
            max_age=604800
        )


class UserAuthenticationView(generics.GenericAPIView, SetAuthenticationCookiesMixin):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.UserAuthenticationSerializer

    def post(self, request):
        serdata = self.serializer_class(data=request.data)
        try:
            serdata.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user = authenticate(email=serdata.data["email"], password=serdata.data["password"])
        if user is not None and user.is_active:
            refresh_token = RefreshToken.for_user(user)
            response = Response({"message": "tokens has been set successfully"}, status=status.HTTP_200_OK)
            self.set_auth_tokens(response, refresh_token)
            return response
        else:
            message = {"detail": "No active account found with the given credentials"}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        response = Response({"message": "Authentication tokens has been destroyed."}, status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        response.delete_cookie("expiry_date")
        return response


class UserRegistrationView(generics.GenericAPIView, SetAuthenticationCookiesMixin):
    serializer_class = serializers.UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        serdata = self.serializer_class(data=request.data)
        serdata.is_valid(raise_exception=True)
        user = serdata.create(serdata.validated_data)
        response = Response({"email": serdata.data["email"]}, status.HTTP_201_CREATED)
        refresh_token = RefreshToken.for_user(user)
        self.set_auth_tokens(response, refresh_token)
        return response


class TokenRefreshView(generics.GenericAPIView, SetAuthenticationCookiesMixin):
    def head(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh_token = RefreshToken(refresh_token)
            access_token = refresh_token.access_token

            response = Response({"message": "Access token refreshed"}, status=status.HTTP_200_OK)
            self.set_access_token(response, access_token)
            return response
        except TokenError:
            return Response({"detail": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
