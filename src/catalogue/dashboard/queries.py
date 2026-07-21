import strawberry
from strawberry_django import connection
from utils.relay import CursorConnection
from .types import CategoryType


@strawberry.type
class CatalogueQuery:
    categories: CursorConnection[CategoryType] = connection(max_results=20)
