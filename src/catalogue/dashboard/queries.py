import strawberry
import strawberry_django
from django.db.models import QuerySet
from strawberry_django import connection

from utils.relay import CursorConnection

from .. import models
from .types import CategoryType


@strawberry.type
class CatalogueQuery:
    categories: CursorConnection[CategoryType] = connection(max_results=20)

    @strawberry_django.connection(CursorConnection[CategoryType], max_results=20)
    def root_categories(self) -> QuerySet[models.Category]:
        """root nodes in the tree"""
        return models.Category.get_root_nodes()
