from strawberry import ID, auto
from strawberry.types import Info
import strawberry_django
from .. import models
from typing import Self
from asgiref.sync import sync_to_async
import strawberry


# @strawberry_django.interface()
# class BaseSeoModelType:
#     pass


@strawberry_django.type(models.CategoryTranslation)
class CategoryTranslation:
    id: auto
    name: auto
    description: auto
    meta_title: auto
    meta_description: auto
    language_code: auto


@strawberry_django.type(models.Category)
class CategoryType:
    id: auto
    name: auto
    slug: auto
    updated_at: auto
    is_public: auto
    ancestors_are_public: auto
    # product: auto
    # translations: auto

    @strawberry_django.field(description="An array of all the node's children")
    async def children(self, info: Info) -> list[Self] | None:  # FIXME  n+1 problem
        return await sync_to_async(list)(self.get_children())
