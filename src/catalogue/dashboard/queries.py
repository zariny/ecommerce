import strawberry
from strawberry_django import field
from .types import CategoryType


@strawberry.type
class CatalogueQuery:
    categories: list[CategoryType] = field()
