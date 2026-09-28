from strawberry.channels import GraphQLWSConsumer
from django.conf import settings

redis = settings.REDIS_CLIENT


class DashboardGraphQLWSConsumer(GraphQLWSConsumer):
    REDIS_HASH_NAME = "online:users"
    CHANNELS_GROUP_NAME = "onlines"

    async def connect(self):
        user = await self.scope["auser"]
        if user.is_authenticated:
            await self.channel_layer.group_add("onlines", self.channel_name)
            conn_count = await redis.hincrby(self.REDIS_HASH_NAME, user.pk, 1)
            if conn_count == 1:
                await self.presence_update()
        return await super().connect()

    async def disconnect(self, code):
        user = await self.scope["auser"]
        if user.is_authenticated:
            await self.channel_layer.group_discard("onlines", self.channel_name)
            conn_count = await redis.hincrby("online:users", user.pk, -1)
            if conn_count <= 0:
                await redis.hdel("online:users", user.pk)
                await self.presence_update()
        return await super().disconnect(code)

    async def presence_update(self):
        count = await redis.hlen(self.REDIS_HASH_NAME)
        await self.channel_layer.group_send(
            self.CHANNELS_GROUP_NAME, {"type": "presence.update", "onlines": count}
        )
