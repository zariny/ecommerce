from django.core.serializers.json import DjangoJSONEncoder
import asyncio, json, io


class Event(object):
    __slots__ = ["data", "event", "id", "retry"]
    _heart_beat = None
    def __init__(self, data, event_type=None, event_id=None, retry=None):
        self.data = data
        self.event= event_type
        self.id = event_id
        self.retry = retry

    @classmethod
    def heartbeat(cls):
        if cls._heart_beat is None:
            cls._heart_beat = cls(data="keep-alive").comment()
        return cls._heart_beat

    def encode(self, json_encode=False):
        if json_encode:
            data = json.dumps(self.data, cls=DjangoJSONEncoder)
        else:
            data = str(self.data)

        buffer = io.StringIO()
        if self.event:
            buffer.write("event: %s\n" % self.event)
        if self.id:
            buffer.write("id: %s\n" % self.id)
        if self.retry:
            buffer.write("retry: %s\n" % self.retry)

        if "\n" in data: # Handle multi-line data
            for line in data.split("\n"):
                buffer.write("data: %s\n" % line)
            buffer.write("\n")
        else:
            buffer.write("data: %s\n\n" % data)
        return buffer.getvalue()

    def comment(self):
        return ": %s\n\n" % str(self.data)


class ServerSentEvent(object):
    def __init__(self, channel=None):
        self.buffer = list()
        self.channel = channel

    def new_event(self, data, event_type="message", json_encode=True):
        self.buffer.append(
            Event(data, event_type).encode(json_encode)
        )

    async def gen(self):
        for event in self.buffer:
            yield event
        self.buffer = list()
        await asyncio.sleep(0)

    def __aiter__(self):
        return self.gen()
