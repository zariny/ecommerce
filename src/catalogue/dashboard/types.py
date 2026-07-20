from strawberry import auto, relay
from strawberry.types import Info
import strawberry_django
from .. import models
from typing import Self
from asgiref.sync import sync_to_async
from utils.types import BaseSeoModelType, ModelWithDescriptionType


async def resolve_tree(instance, method_name: str):
    method = getattr(instance, method_name)
    return await sync_to_async(lambda: list(method()))()


@strawberry_django.filter_type(models.Category, lookups=True)
class CategoryFilterType:
    is_public: auto
    ancestors_are_public: auto
    slug: auto
    updated_at: auto


@strawberry_django.order_type(models.Category)
class CategoryOrderType:
    updated_at: auto

    @strawberry_django.order_field(
        description="Order by tree hierarchy structure (materialized path)"
    )
    def hierarchy(self, value: strawberry_django.Ordering, prefix: str) -> list[str]:
        return [value.resolve(f"{prefix}path")]


@strawberry_django.type(models.CategoryTranslation)
class CategoryTranslation:
    id: auto
    name: auto
    description: auto
    meta_title: auto
    meta_description: auto
    language_code: auto


@strawberry_django.type(
    models.Category, filters=CategoryFilterType, ordering=CategoryOrderType
)
class CategoryType(relay.Node, BaseSeoModelType, ModelWithDescriptionType):
    name: auto
    slug: auto
    updated_at: auto
    is_public: auto
    ancestors_are_public: auto
    background: auto
    background_caption: auto
    # product: auto
    # translations: auto

    @strawberry_django.field(
        description="Children of this node",
        only=["path", "depth", "numchild"],
    )
    async def children(self, info: Info) -> list[Self]:
        return await resolve_tree(self, "get_children")

    @strawberry_django.field(
        description="Ancestors of this node",
        only=["path", "depth", "numchild"],
    )
    async def ancestors(self, info: Info) -> list[Self]:
        return await resolve_tree(self, "get_ancestors")
