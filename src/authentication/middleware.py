from django.http.cookie import parse_cookie
from abc import ABCMeta
import jwt
from inspect import iscoroutinefunction, markcoroutinefunction
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from account.models import User
from .tokens import JWTToken
from asgiref.sync import sync_to_async


class AbstractHybridMiddleware(metaclass=ABCMeta):
    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        self.async_mode = iscoroutinefunction(self.get_response)
        if self.async_mode:
            markcoroutinefunction(self)

    def __call__(self, request):
        raise NotImplementedError

    async def __acall__(self, request):  # Django convention
        raise NotImplementedError


class JWTCookieAuthMiddleware(AbstractHybridMiddleware):
    EXEMPT_PATH_PREFIXES = JWTToken.conf["JWT_AUTH_EXEMPT_PATHS"]

    def __call__(self, request):
        if self.async_mode:
            return self.__acall__(request)
        self._attach(request)
        return self.get_response(request)

    async def __acall__(self, request):
        self._attach(request)
        return await self.get_response(request)

    def _attach(self, request):
        if self.is_exempt(request):
            return
        request.user = SimpleLazyObject(lambda: self.user(request))

        async def auser():
            if not hasattr(request, "_jwt_cached_user"):
                await sync_to_async(self.user)(request)
            return request._jwt_cached_user

        request.auser = auser

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


class AbstractJWTMiddleware(metaclass=ABCMeta):
    async def __call__(self):
        raise NotImplementedError

    async def __acall__(self):  # Django convention
        raise NotImplementedError

    def pars_token(self, cookies):
        token = cookies.get("access")
        if not token:
            return None
        try:
            payload = JWTToken(token).payload
        except jwt.ExpiredSignatureError, jwt.InvalidTokenError:
            return None

        if payload.get("token_type") == "access":
            return payload
        return None


class ChannelsJWTMiddleware(AbstractJWTMiddleware):
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, recive, send):
        headers = dict(scope["headers"])
        cookies = parse_cookie(headers.get(b"cookie", b"").decode())
        payload = self.pars_token(cookies)
        scope["auser"] = LazyUser(payload)
        return await self.app(scope, recive, send)


async def aget_user(payload=None):
    if payload is None:
        return AnonymousUser()
    pk = payload.get("user_id", None)
    if pk is not None:
        try:
            return await User.objects.aget(pk=pk)
        except User.DoesNotExist:
            pass
    return AnonymousUser()


class LazyUser:
    def __init__(self, payload):
        self.payload = payload
        self._user = None  # cache user to avoid multi queries per a request

    def __await__(self):
        async def resolve():
            if self._user is None:
                self._user = await aget_user(self.payload)
            return self._user

        return resolve().__await__()
