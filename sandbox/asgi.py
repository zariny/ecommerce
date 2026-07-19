"""
ASGI config for ecommerce project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
# from middleware.authentication import JWTCookieAuthMiddleware
# from account.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sandbox.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": JWTCookieAuthMiddleware(
    #     URLRouter(websocket_urlpatterns)
    # ),
})
