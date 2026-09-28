import os

from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter
from strawberry.channels import GraphQLWSConsumer


# NOTE: Call get_asgi_application() before importing GraphQL schemas to ensure Django initializes INSTALLED_APPS before schema imports.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sandbox.settings")
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from authentication.middleware import ChannelsJWTMiddleware
from utils.consumers import DashboardGraphQLWSConsumer
from sandbox.schema.public import schema as public_schema
from sandbox.schema.dashboard import schema as dashboard_schema


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": URLRouter(
            [
                path(
                    "graphql/",
                    GraphQLWSConsumer.as_asgi(
                        schema=public_schema,
                    ),
                ),
                path(
                    "dashboard/graphql/",
                    ChannelsJWTMiddleware(
                        DashboardGraphQLWSConsumer.as_asgi(
                            schema=dashboard_schema,
                        )
                    ),
                ),
            ]
        ),
    }
)
