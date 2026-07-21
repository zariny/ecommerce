import strawberry
from strawberry_django import BaseFilterLookup, relay
from strawberry.relay.types import NodeType


@strawberry.type(name="CursorConnection")
class CursorConnection(relay.DjangoCursorConnection[NodeType]):
    DEFAULT_FIRST = 10
    """
    HACK Pagination exists to limit how much data a client can pull per
    request. But relay allows omitting both `first` and `last`,
    in which case the library returns ALL results unlimited —
    `max_results` only caps an explicit value, it doesn't enforce one.

    Since the library provides no built-in way to force a default
    page size, we override `resolve_connection` to fall back to
    DEFAULT_FIRST when neither argument is given.
    """

    @classmethod
    def resolve_connection(
        cls, nodes, *, info, before=None, after=None, first=None, last=None, **kwargs
    ):
        if first is None and last is None:
            first = cls.DEFAULT_FIRST
        return super().resolve_connection(
            nodes,
            info=info,
            before=before,
            after=after,
            first=first,
            last=last,
            **kwargs,
        )


@strawberry.input
class BaseFilter:
    id: BaseFilterLookup[strawberry.relay.GlobalID]
