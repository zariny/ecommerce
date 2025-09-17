from django.test import TransactionTestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from channels.testing import WebsocketCommunicator
from account.consumers import OnlineUserCountConsumer


User = get_user_model()


TEST_CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
}

@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
class TestOnlineUserCountConsumer(TransactionTestCase):
    # NOTE Each test runs inside its own event‑loop

    def setUp(self):
        self.staff_user = User._default_manager.create_superuser(
            email="superuser@email.com",
            password="strong-password"
        )
        self.path = r"ws/online/$"
        cache.set("online_user_count", 0)


    async def test_staff_users(self):
        communicator = WebsocketCommunicator(OnlineUserCountConsumer.as_asgi(), path=r"ws/online/$")
        communicator.scope["user"] = self.staff_user
