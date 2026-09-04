import strawberry
from strawberry_django import connection, node
from utils.relay import CursorConnection
from . import types


@strawberry.type
class ProductQuery:
    products: CursorConnection[types.ProductType] = connection()
    product: types.ProductType = node()
    product_classes: CursorConnection[types.ProductClassType] = connection()
    attributes: CursorConnection[types.AttributeType] = connection()
    variants: CursorConnection[types.ProductVariantType] = connection()
