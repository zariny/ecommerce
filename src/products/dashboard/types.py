from strawberry import auto, lazy
from strawberry.relay import Node
import strawberry_django
from utils.types import BaseSeoModelType, ModelWithDescriptionType, TranslationModelType
from .. import models
from typing import Annotated, TYPE_CHECKING


if TYPE_CHECKING:
    from catalogue.dashboard.types import CategoryType


@strawberry_django.type(models.Product)
class ProductType(Node, BaseSeoModelType, ModelWithDescriptionType):
    title: auto
    slug: auto
    is_public: auto
    created_at: auto
    updated_at: auto
    categories: list[Annotated["CategoryType", lazy("catalogue.dashboard.types")]]
    translations: list["ProductTranslateType"]
    # attributes:
    # product_type:


class ProductClassType: ...


@strawberry_django.type(models.ProductTranslate)
class ProductTranslateType(Node, TranslationModelType):
    title: auto
    description: auto
