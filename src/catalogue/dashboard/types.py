from typing import TYPE_CHECKING, Annotated, Optional, Self

import strawberry_django
from asgiref.sync import sync_to_async
from strawberry import UNSET, auto, lazy, relay
from strawberry.relay import GlobalID
from strawberry.types import Info
from strawberry_django import BaseFilterLookup

from utils.types import (
    BaseSeoModelType,
    ModelWithDescriptionType,
    TranslationModelType,
)

from .. import models

if TYPE_CHECKING:
    from products.dashboard.types import ProductType


async def resolve_tree(instance, method_name: str):
    method = getattr(instance, method_name)
    return await sync_to_async(lambda: list(method()))()


@strawberry_django.filter_type(models.Category, lookups=True)
class CategoryFilterType:
    id: Optional[BaseFilterLookup[GlobalID]] = UNSET
    is_public: auto
    ancestors_are_public: auto
    name: auto
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
class CategoryTranslationType(relay.Node, TranslationModelType):
    name: auto
    description: auto


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
    numchild: auto
    products: list[Annotated["ProductType", lazy("products.dashboard.types")]]
    translations: list[CategoryTranslationType]

    @strawberry_django.field(
        description="all direct children of this node",
        only=["path", "depth", "numchild"],
    )
    async def children(self, info: Info) -> list[Self]:  # FIXME n+1 query problem :(
        return await resolve_tree(self, "get_children")

    @strawberry_django.field(
        description="Ancestors of this node",
        only=["path", "depth", "numchild"],
    )
    async def ancestors(self, info: Info) -> list[Self]:  # FIXME n+1 query problem :(
        return await resolve_tree(self, "get_ancestors")
