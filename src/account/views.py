from django.contrib.auth import get_user_model, authenticate
from django.utils.timezone import localtime
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
            max_age=refresh_token.lifetime.total_seconds()
        )
        self.set_access_token(response, refresh_token)

    def set_access_token(self, response, refresh_token):
        access_token = refresh_token.access_token
        access_token_expiry = localtime(access_token.current_time).strftime("%Y-%m-%dT%H:%M:%SZ")
        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,
            samesite="Lax",
            max_age=access_token.lifetime.total_seconds()
        )
        response.set_cookie(
            key="expiry_date",
            value=access_token_expiry,
            httponly=False,
            samesite="Lax",
            max_age=refresh_token.lifetime.total_seconds()
        )


class UserAuthenticationView(generics.GenericAPIView, SetAuthenticationCookiesMixin):
    """
    User Authentication View.
    (POST) and (DELETE)
    This view handles user login and logout.

    POST:
        Authenticates a user based on email and password.
        Returns a 200 OK response with a success message and sets authentication cookies
        (access_token, refresh_token, expiry_date) upon successful authentication.
        Returns a 401 Unauthorized response if authentication fails.

        Request body (JSON):
            - email (string, required): User's email address.
            - password (string, required): User's password.

        Response (200 OK):
            - message (string): user email

        Response (401 Unauthorized):
            - detail (string): "No active account found with the given credentials"

    DELETE:
        Logs out the user by deleting the authentication cookies.
        Returns a 200 OK response with a success message.

        Request body: None

        Response (200 OK):
            - message (string): "Authentication tokens has been destroyed."

    Authentication:
        This endpoint does not require any authentication to be accessed.

    Cookies:
        - access_token (HTTPOnly):  Short-lived access token for API authorization.
        - refresh_token (HTTPOnly): Long-lived refresh token for obtaining new access tokens.
        - expiry_date:  The expiry date of the access token.  This is *not* HTTPOnly, and has  format.
    """
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
            response = Response({"email": serdata.data["email"]}, status=status.HTTP_200_OK)
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
    """
    User Registration View.
    (POST) This view handles user registration.
        Creates a new user account.
        Returns a 201 Created response with the user's email and sets authentication cookies
        (access_token, refresh_token, expiry_date) upon successful registration.

        Request body (JSON):
            - email (string, required): User's email address.
            - password (string, required): User's password.

        Response (201 Created):
            - email (string): The registered user's email address.

    Authentication:
        This endpoint does not require any authentication to be accessed.

    Cookies:
        - access_token (HTTPOnly):  Short-lived access token for API authorization.
        - refresh_token (HTTPOnly): Long-lived refresh token for obtaining new access tokens.
        - expiry_date:  The expiry date of the access token.  This is *not* HTTPOnly, and has ISO 8601 format.
    """
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
    """
    Token Refresh View.
    (HEAD)
    This view handles refreshing access tokens using a refresh token.

    Retrieves the refresh token from the `refresh_token` cookie.
        If the refresh token is valid, it generates a new access token and sets it in the `access_token` cookie.
        Returns a 200 OK response.
        Returns a 401 Unauthorized response if the refresh token is invalid or missing.

        Request body: None

        Response (200 OK):
            - detail (string): "Access token refreshed"

        Response (401 Unauthorized):
            - detail (string): "Invalid or expired refresh token"

    Authentication:
        This endpoint relies on the `refresh_token` cookie for authentication.
    Cookies:
        - access_token (HTTPOnly):  Short-lived access token for API authorization.
        - refresh_token (HTTPOnly): Long-lived refresh token for obtaining new access tokens.
        - expiry_date:  The expiry date of the access token.  This is *not* HTTPOnly, and has ISO 8601 format.
    """
    def head(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh_token = RefreshToken(refresh_token)

            response = Response({"detail": "Access token refreshed"}, status=status.HTTP_200_OK)
            self.set_access_token(response, refresh_token)
            return response
        except TokenError:
            return Response({"detail": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
