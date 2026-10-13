import datetime as dt
import strawberry
import strawberry_django
from django.db.models import QuerySet, Count
from utils.relay import CursorConnection
from utils.charts import SimpleChart, NumericPoint
from permissions.integrations import with_permission
from .. import models
from ..permissions import CataloguePermission as P
from .types import CategoryType


@with_permission(P.CATALOGUE_MANAGER)
@strawberry.type
class CatalogueQuery:
    categories: CursorConnection[CategoryType] = strawberry_django.connection(
        max_results=20
    )

    @strawberry_django.connection(CursorConnection[CategoryType], max_results=20)
    def root_categories(self) -> QuerySet[models.Category]:
        """root nodes in the tree"""
        return models.Category.get_root_nodes()

    @strawberry_django.field
    def top_ten_categories_chart(self) -> SimpleChart:
        qs = (
            models.Category.objects.values("id", "name")
            .annotate(product_count=Count("products"))
            .order_by("-product_count")[:10]
        )

        return SimpleChart(
            title="some title",
            generated_at=dt.datetime.now(tz=dt.UTC),
            lines=[NumericPoint(label=r["name"], num=r["product_count"]) for r in qs],
        )
