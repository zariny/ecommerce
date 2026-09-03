import strawberry
import jwt
from enum import StrEnum, auto
from datetime import datetime, UTC
from strawberry.types import Info
from django.contrib.auth import aauthenticate, get_user_model

from permissions.models import Permission
from .tokens import JWTToken


User = get_user_model()


class AuthStatus(StrEnum):
    SUCCESS = auto()
    REFRESH_TOKEN_MISSING = auto()
    REFRESH_TOKEN_EXPIRED = auto()
    USER_NOT_FOUND = auto()
    ACCOUNT_DISABLED = auto()
    INVALID_TOKEN_TYPE = auto()
    INVALID_REFRESH_TOKEN = auto()
    INVALID_CREDENTIALS = auto()


@strawberry.type
class AuthDetail:
    ok: bool
    status: AuthStatus
    message: str = ""
    expire_date: datetime | None = None


ACCESS_TOKEN_LIFETIME = JWTToken.conf.get("ACCESS_TOKEN_LIFETIME")
REFRESH_TOKEN_LIFETIME = JWTToken.conf.get("REFRESH_TOKEN_LIFETIME")


@strawberry.type
class AuthenticateMutation:
    @strawberry.mutation
    async def login(self, info: Info, email: str, password: str) -> AuthDetail:
        user = await aauthenticate(username=email, password=password)
        if user is None:
            return AuthDetail(
                ok=False,
                status=AuthStatus.INVALID_CREDENTIALS,
                message="Incorrect username or password.",
            )
        response = info.context.response

        permissions = await Permission.auser_permissions(user)
        permissions = [perm.codename for perm in permissions]

        refresh_token = JWTToken.new_refresh_token(user.pk)
        access_token = JWTToken.new_access_token(user.pk, permissions)

        response.set_cookie(
            key="refresh",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=int(REFRESH_TOKEN_LIFETIME.total_seconds()),
            # path=JWT.conf.get(
            #     "REFRESH_COOKIE_PATH"
            # ),  # TODO Use a unique URL path to access the refresh token.
        )

        response.set_cookie(
            key="access",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=int(ACCESS_TOKEN_LIFETIME.total_seconds()),
        )
        return AuthDetail(
            ok=True,
            status=AuthStatus.SUCCESS,
            message="Logged in successfully.",
            expire_date=datetime.now(UTC) + ACCESS_TOKEN_LIFETIME,
        )

    @strawberry.mutation
    async def logout(self, info: Info) -> AuthDetail:
        response = info.context.response
        response.delete_cookie("refresh")
        response.delete_cookie("access")
        return AuthDetail(
            message="Logged out successfully.", status=AuthStatus.SUCCESS, ok=True
        )

    @strawberry.mutation
    async def refresh(self, info: Info) -> AuthDetail:
        request = info.context.request
        response = info.context.response

        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            return AuthDetail(
                ok=False,
                status=AuthStatus.REFRESH_TOKEN_MISSING,
                message="Refresh token not found.",
            )

        try:
            payload = JWTToken(refresh_token).payload
        except jwt.ExpiredSignatureError:
            return AuthDetail(
                ok=False,
                status=AuthStatus.REFRESH_TOKEN_EXPIRED,
                message="Refresh token expired.",
            )
        except jwt.InvalidTokenError:
            return AuthDetail(
                ok=False,
                status=AuthStatus.INVALID_REFRESH_TOKEN,
                message="Invalid refresh token.",
            )

        if payload.get("token_type") != "refresh":
            return AuthDetail(
                ok=False,
                status=AuthStatus.INVALID_TOKEN_TYPE,
                message="The token type is invalid. Send a refresh token.",
            )

        try:
            user = await User.objects.aget(pk=payload["user_id"])
        except User.DoesNotExist:
            return AuthDetail(
                ok=False,
                status=AuthStatus.USER_NOT_FOUND,
                message="User no longer exists.",
            )

        permissions = await Permission.auser_permissions(user)
        permissions = [perm.codename for perm in permissions]

        new_access_token = JWTToken.new_access_token(user.pk, permissions)

        response.set_cookie(
            key="access",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=int(ACCESS_TOKEN_LIFETIME.total_seconds()),
        )

        return AuthDetail(
            ok=True,
            status=AuthStatus.SUCCESS,
            message="Token refreshed successfully.",
            expire_date=datetime.now(UTC) + ACCESS_TOKEN_LIFETIME,
        )
