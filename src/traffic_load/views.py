from utils.views import ServerSentEventView
from utils.authenticate import JWTCookiesBaseAuthentication
from rest_framework.permissions import IsAdminUser
from utils.server_sent_event import Event
from django_redis import get_redis_connection
import asyncio
import time


redis_conn = get_redis_connection("default")


class TraficAnalyzerView(ServerSentEventView):
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (IsAdminUser,)

    async def stream(self, request, *args, **kwargs):
        ttl = 20
        while True:
            now = time.time()
            redis_conn.zremrangebyscore("_users", "-inf", now - ttl)
            redis_conn.zremrangebyscore("_anon", "-inf", now - ttl)
            user_count = redis_conn.zcard("_users")
            anon_count = redis_conn.zcard("_anon")
            yield Event(
                data={"user_count": user_count, "anon_count": anon_count},
                event_type="message"
            ).encode(json_encode=True)
            await asyncio.sleep(2)
