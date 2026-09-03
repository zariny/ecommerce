import jwt
from inspect import iscoroutinefunction, markcoroutinefunction
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from account.models import User
from .tokens import JWTToken


class JWTCookieAuthMiddleware:
    sync_capable = True
    async_capable = True
    EXEMPT_PATH_PREFIXES = JWTToken.conf["JWT_AUTH_EXEMPT_PATHS"]

    def __init__(self, get_response):
        self.get_response = get_response

        self.async_mode = iscoroutinefunction(self.get_response)

        if self.async_mode:
            markcoroutinefunction(self)

    def __call__(self, request):
        if self.async_mode:
            return self.__acall__(request)
        if not self.is_exempt(request):
            request.user = SimpleLazyObject(lambda: self.user(request))

        return self.get_response(request)

    async def __acall__(self, request):  # Django convention
        if self.is_exempt(request):
            return await self.get_response(request)

        async def _auser():
            return await self.auser(request)

        request.auser = _auser
        return await self.get_response(request)

    def user(self, request):
        if hasattr(request, "_jwt_cached_user"):
            return request._jwt_cached_user

        payload = self.access_token(request)
        if payload is None:
            request._jwt_cached_user = AnonymousUser()
            return request._jwt_cached_user

        try:
            user = User.objects.get(pk=payload["user_id"])
        except User.DoesNotExist:
            request._jwt_cached_user = AnonymousUser()
        else:
            user.token_permissions = set(payload.get("perms", []))
            request._jwt_cached_user = user
        return request._jwt_cached_user

    async def auser(self, request):
        if hasattr(request, "_jwt_async_cached_user"):
            return request._jwt_async_cached_user

        payload = self.access_token(request)
        if payload is None:
            request._jwt_async_cached_user = AnonymousUser()
            return request._jwt_async_cached_user

        try:
            user = await User.objects.aget(pk=payload["user_id"])
        except User.DoesNotExist:
            request._jwt_async_cached_user = AnonymousUser()
            return request._jwt_async_cached_user

        user.token_permissions = set(payload.get("perms", []))
        request._jwt_async_cached_user = user
        return request._jwt_async_cached_user

    def access_token(self, request) -> dict | None:
        token = request.COOKIES.get("access")
        if not token:
            return None

        try:
            payload = JWTToken(token).payload
        except jwt.ExpiredSignatureError, jwt.InvalidTokenError:
            return None

        if payload.get("token_type") == "access":
            return payload
        return None

    def is_exempt(self, request) -> bool:
        return request.path.startswith(self.EXEMPT_PATH_PREFIXES)
