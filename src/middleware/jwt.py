from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.db import close_old_connections


User = get_user_model()


class JWTCookieAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope.get('headers', []))
        access_token = None
        if b'cookie' in headers:
            cookies = headers[b'cookie'].decode()
            for cookie in cookies.split(';'):
                if 'access_token' in cookie:
                    access_token = cookie.split('=')[1].strip()
                    break

        scope['user'] = AnonymousUser()

        if access_token:
            try:
                validated_token = AccessToken(access_token)
                user = await self.get_user(validated_token)
                if user:
                    scope['user'] = user
            except Exception:
                pass

        return await super().__call__(scope, receive, send)

    @staticmethod
    async def get_user(validated_token):
        try:
            user_id = validated_token.get('user_id')
            user = await User.objects.aget(id=user_id)
            close_old_connections()
            return user
        except User.DoesNotExist:
            return None
