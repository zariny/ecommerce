from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
import json


class OnlineUserCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        count = cache.get("online_user_count", 0)
        cache.set("online_user_count", count + 1)
        user = self.scope["user"]
        if user.is_authenticated and user.is_staff:
            await self.channel_layer.group_add("admin_users", self.channel_name)

        await self.channel_layer.group_send("admin_users", {
            "type": "send_online_count",
            "count": cache.get("online_user_count", 0),
        })

    async def disconnect(self, code):
        count = cache.get("online_user_count", 0)
        count = max(0, count - 1)
        cache.set("online_user_count", count)
        user = self.scope["user"]
        if user.is_authenticated and user.is_staff:
            await self.channel_layer.group_discard("admin_users", self.channel_name)

        await self.channel_layer.group_send("admin_users", {
            "type": "send_online_count",
            "count": cache.get("online_user_count", 0),
        })


    async def send_online_count(self, event):
        await self.send(json.dumps({
            "online_users": event["count"]
        }))
