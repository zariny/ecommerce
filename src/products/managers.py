from django.db import connection, models
from django.db.models.constants import LOOKUP_SEP


class ProductAttributeFilterDict(dict):
    def __init__(self, **filters):
        super().__init__()
        for key, value in filters.items():
            if LOOKUP_SEP in key:
                field, lookup = key.split(LOOKUP_SEP, 1)
                self[field] = (lookup, value)
            else:
                self[key] = (None, value)

    def _Q_object(self, lookup, value):
        kwargs = {}
        key = "attribute_values__value__value"
        if lookup:
            key = f"{key}{LOOKUP_SEP}{lookup}"
        kwargs[key] = value
        return models.Q(**kwargs)

    def querying(self, queryset):
        qs = queryset
        for slug, (lookup, value) in self.items():
            selected_values = self._Q_object(lookup, value)
            if not selected_values:
                return queryset.none()
            qs = qs.filter(selected_values, attribute_values__attribute__slug=slug)

        return qs


class ProductManager(models.Manager):
    def filter_by_attribute(self, **kwargs):
        """
        Allows querying by attribute:
            Product.objects.filter_by_attribute(<ProductAttribute>=<value>,<ProductAttribute>__lookups=<value>)
            Product.objects.filter_by_attribute(size="XL", color__in=["red", "blue"])
        """
        query_filter = ProductAttributeFilterDict(**kwargs)
        return query_filter.querying(self)

    def browsable(self):
        return self.filter(is_public=True)


class ProductClassManager(models.Manager):
    def get_ancestor_ids(self, product_class_id: int):  # XXX neads test
        sql = """
        WITH RECURSIVE ancestors AS (
            SELECT
                parent_id,
                1 AS depth
            FROM products_productclassedge
            WHERE child_id = %s

            UNION ALL

            SELECT
                edge.parent_id,
                a.depth + 1
            FROM products_productclassedge edge
            INNER JOIN ancestors a
                ON edge.child_id = a.parent_id
        )
        SELECT
            parent_id,
            MIN(depth) AS depth
        FROM ancestors
        GROUP BY parent_id
        ORDER BY depth ASC;
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, [product_class_id])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_descendant_ids(self, product_class_id: int):
        sql = """
            WITH RECURSIVE descendants AS (
                SELECT
                    child_id,
                    1 AS depth
                FROM products_productclassedge
                WHERE parent_id = %s

                UNION ALL

                SELECT
                    edge.child_id,
                    d.depth + 1
                FROM products_productclassedge edge
                INNER JOIN descendants d
                    ON edge.parent_id = d.child_id
            )
            SELECT
                child_id,
                MIN(depth) AS depth
            FROM descendants
            GROUP BY child_id
            ORDER BY depth ASC;
            """

    def check_cycle(self, parent_id: int, child_id: int) -> bool:
        pass
