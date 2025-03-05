from django.db.models import F, QuerySet
from django.utils.functional import cached_property
ProductAttributeValue = ...  # Placeholder to avoid import error; used only for documentation.


class AttributeCache(dict):
    def __init__(self, product):
        self.product = product
        self._attribute_value_iterator = None
        self.pks = list(self.attribute_value.values_list("attribute__pk", flat=True))

    @cached_property
    def attribute_value(self) -> QuerySet[ProductAttributeValue]:
        return self.product.attribute_values.select_related("attribute").annotate(
            code=F("attribute__slug"),
            value_type=F("attribute__value_type")
        )

    def attribute_value_iterator(self):
        if self._attribute_value_iterator is None:
            self._attribute_value_iterator = self.attribute_value.iterator()
        return self._attribute_value_iterator

    def get(self, attribute_code, default=None):
        try:
            return self[attribute_code]
        except KeyError:
            for att_val in self.attribute_value_iterator():
                code = att_val.code
                self[code] = att_val
                if code == attribute_code:
                    return att_val
        return default


class ProductAttributeContainer:
    def __init__(self, model_instance):
        # WARNING: This method is called during the initialization of a product instance,
        #  so it should be cheap and have very lazy behavior.
        self.product = model_instance
        self._cache = None
        self._dirty = []

    def all(self) -> QuerySet[ProductAttributeValue]:
        return self.cache().attribute_value

    def cache(self):
        if self._cache is None:
            self._cache =  AttributeCache(self.product)
        return self._cache

    def invalidate(self):
        self._cache = None

    def proper_save(self):
        to_be_update = []
        to_be_create = []
        to_be_deleted = []

        ProductAttributeValue = self.product.attribute_values.model
        for attr_val in self._dirty:
            if attr_val["attribute"].pk in self.cache().pks:
                attribute = self.cache().get(attr_val["attribute"].slug)
                attribute.value = attr_val["value"]
                to_be_update.append(attribute)
                self.cache().pks.remove(attr_val["attribute"].pk)
            else:
                to_be_create.append(ProductAttributeValue(product=self.product, **attr_val))

        for i in self.cache().pks:
            to_be_deleted.append(i)

        return  to_be_update, to_be_create, to_be_deleted

    def save(self):
        to_be_update, to_be_create,  to_be_deleted = self.proper_save()
        if to_be_update:
            self.product.attribute_values.bulk_update(to_be_update, fields=["value"])
        if to_be_create:
            self.product.attribute_values.bulk_create(to_be_create)
        if to_be_deleted:
            self.product.attribute_values.filter(product=self.product, attribute__pk__in=to_be_deleted).delete()

        self._cache = None
