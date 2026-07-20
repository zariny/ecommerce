import strawberry
from strawberry_django import connection
from strawberry_django.relay import DjangoCursorConnection
from .types import CategoryType


@strawberry.type
class CatalogueQuery:
    categories: DjangoCursorConnection[CategoryType] = connection(max_results=10)
