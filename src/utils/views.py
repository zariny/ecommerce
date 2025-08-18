import asyncio
from typing import AsyncGenerator
from django.http import StreamingHttpResponse
from django.views import View
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import generics
from .server_sent_event import ServerSentEvent, Event
from . import permissions, authenticate


class ListLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 30


class BaseAdminView(generics.ListCreateAPIView):
    authentication_classes = (authenticate.JWTCookiesBaseAuthentication,)
    permission_classes = (permissions.AdminAndModelLevelPermission,)
    pagination_class = ListLimitOffsetPagination


class BaseAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (authenticate.JWTCookiesBaseAuthentication,)
    permission_classes = (permissions.AdminAndModelLevelPermission,)


SSE_CONTENT_TYPE = 'text/event-stream'


class ServerSentEventView(View):
    def dispatch(self, request, *args, **kwargs):
        self.sse = ServerSentEvent()
        res =  StreamingHttpResponse(self._stream(request, *args, **kwargs), content_type=SSE_CONTENT_TYPE)
        res.headers["Cache-Control"] = "no-cache"
        res.headers["Connection"] = "keep-alive"
        return res

    async def _stream(self, request, *args, **kwargs):
        stream = self.stream(request, *args, **kwargs)
        queue = asyncio.Queue()
        SENTINEL = object()
        async def producer():
            async for event in stream:
                await queue.put(event)
            await queue.put(SENTINEL)

        async with asyncio.TaskGroup() as tg:
            tg.create_task(producer())
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=20)
                except asyncio.TimeoutError:
                    yield Event.heartbeat()
                    continue
                if event is SENTINEL:
                    return
                elif isinstance(event, ServerSentEvent):
                    async for item in event:
                        yield item
                else:
                    yield event


    async def stream(self, request, *args, **kwargs) -> AsyncGenerator[Event | ServerSentEvent, None]:
        raise NotImplementedError("You must implement `stream` AsyncGenerator in your sse cbv.")
