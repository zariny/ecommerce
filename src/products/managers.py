from django.db import models
from models.constants import LOOKUP_SEP


class AttributeFilter(dict):
    def __init__(self, **filters):
        super().__init__(**filters)
        self.filters = filters

        for key, value in self.filters.items():
            if LOOKUP_SEP in key:
                # has lookup
                ...
            else:
                field_name = key



class ProductQuerySet(models.QuerySet):
    def filter_by_attributes(self, **kwargs):
        """
        Product.objects.filter_by_attributes(<ProductAttribute>=<value>, <ProductAttribute>__lookups=<value>)
        """
        ...
