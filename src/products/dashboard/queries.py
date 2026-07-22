import strawberry
from strawberry_django import connection
from .types import ProductType
from utils.relay import CursorConnection


@strawberry.type
class ProductQuery:
    products: CursorConnection[ProductType] = connection(max_results=20)
