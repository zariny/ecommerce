from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from uuid import uuid4
import time


class UserActivityTracker:
    cache_client = cache.client.get_client(write=True)
    _anonymous_users_set_name = "_anon"
    _login_users_set_name = "_users"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.jwt_pk is not None:
            self.cache_client.zadd(
                self._login_users_set_name,
                {request.jwt_pk: round(time.time())}
            )
        elif request.COOKIES.get("_anon", False):
            key = request.COOKIES.get("_anon")
            self.cache_client.zadd(
                self._anonymous_users_set_name,
                {key: round(time.time())}
            )

        else:
            response = self.get_response(request)
            anon_id = uuid4()
            response.set_cookie(
                key="_anon",
                value=anon_id,
                httponly=True,
                samesite="None",
                secure=True,
                max_age=36000
            )
            self.cache_client.zadd(
                self._anonymous_users_set_name,
                {anon_id: round(time.time())}
            )

            return response
        response = self.get_response(request)
        return response
