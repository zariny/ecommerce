from django.db import models
from django.utils.functional import cached_property


class AttributeCache(dict):
    def __init__(self, product):
        self.product = product

    def get(self, attribute, default=None):
        try:
            return self[attribute]
        except KeyError:
            for item in self.query:
                attribute_slug = item.slug
                attribute_value = item.value
                self[attribute_slug] = attribute_value
                if attribute_slug == attribute:
                    return attribute_value
        return default

    @cached_property
    def query(self):
        qs = self.product.attribute_values.annotate(slug=models.F("attribute__slug"))
        return qs.iterator()


class ProductAttributeContainer:
    RESERVED_ATTRIBUTE_NAMES = {
        "_product",
        "_cache",
        "_dirty",
        "save",
        "invalidate",
    }

    def __init__(self, model_instance):
        self.__dict__.update(
            {
                "_product": model_instance,
                "_cache": AttributeCache(model_instance),
                "_dirty": dict()
            }
        )

    def __setattr__(self, key, value):
        """
        set a product attribute via attr:
            <Product-instance>.attr.<attribute-name> = <value>
        """
        if key not in ProductAttributeContainer.RESERVED_ATTRIBUTE_NAMES:
            self._dirty.update(
                {key: value}
            )
        else:
            raise NameError("name <%s> has been reserved by class." % key)

    def __getattribute__(self, item):
        """
            >>> hat = Product.objects.get(name="hat")
            >>> hat.attr.color
            "red"
        """
        if item in ProductAttributeContainer.RESERVED_ATTRIBUTE_NAMES or item.startswith("__"):
            return super().__getattribute__(item)
        return self._cache.get(item)

    def __getattr__(self, item):
        pass

    def save(self):
        """
        save all changes for a product
            some new attributes must be saved or some others must be updated and...
        """

    def invalidate(self):
        self._cache = AttributeCache(self._product)
