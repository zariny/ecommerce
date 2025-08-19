from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
import time


class RecordConnectionMiddleware(MiddlewareMixin):
    cache_client = cache.client.get_client(write=True)
    _set_name = "onlines"

    def process_request(self, request):
        if request.jwt_pk is not None:
            key = "user_%s" % request.jwt_pk
            self.cache_client.zadd(
                self._set_name,
                {key: round(time.time())}
            )
        elif request.COOKIES.get(settings.CSRF_COOKIE_NAME):
            key = "anon_%s" % request.COOKIES.get(settings.CSRF_COOKIE_NAME)
            self.cache_client.zadd(
                self._set_name,
                {key: round(time.time())}
            )
