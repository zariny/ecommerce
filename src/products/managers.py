from django.db import models
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
        kwargs = dict()
        key = "attribute_values__value__value"
        if lookup:
            key = "%s%s%s" % (key, LOOKUP_SEP, lookup)
        kwargs[key] = value
        return models.Q(**kwargs)

    def querying(self, queryset):
        qs = queryset
        for slug, (lookup, value) in self.items():
            selected_values = self._Q_object(lookup, value)
            if not selected_values:
                return queryset.none()
            qs = qs.filter(
                selected_values,
                attribute_values__attribute__slug=slug
            )

        return qs


class ProductQuerySet(models.QuerySet):
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
