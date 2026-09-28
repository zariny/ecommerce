import strawberry
from django.conf import settings
from collections.abc import AsyncGenerator
from strawberry.types import Info
from strawberry.permission import BasePermission

redis = settings.REDIS_CLIENT


@strawberry.type
class UserOnlineCount:
    onlines: int


class IsAuthenticated(BasePermission):
    message = "Authentication required."

    async def has_permission(self, source, info, **kwargs):
        user = await info.context["ws"].scope["auser"]
        return user.is_authenticated


@strawberry.type
class AccountSubscription:
    @strawberry.subscription(permission_classes=[IsAuthenticated])
    async def user_online_counts(self, info: Info) -> AsyncGenerator[UserOnlineCount]:
        ws = info.context["ws"]
        async with ws.listen_to_channel(
            type="presence.update", groups=["onlines"]
        ) as messages:
            count = await redis.hlen("online:users")
            yield UserOnlineCount(onlines=count)
            async for message in messages:
                yield UserOnlineCount(onlines=message["onlines"])
