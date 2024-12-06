from core.models import ModelWithDescription, BaseSeoModel, ModelWithMetadata
from django.db import models
from .utils import VALUE_TYPE_CHOICE
from .fields import DynamicValueField
from src.core.models import TranslationModel


class ProductClass(ModelWithMetadata):
    title = models.CharField(max_length=250, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, auto_created="title", db_index=True)
    require_shipping = models.BooleanField(default=True)
    track_stock = models.BooleanField(default=True)


    class Meta:
        app_label = "products"


    def __str__(self):
        return self.title or self.slug

    def __repr__(self):
        return "<%s> obj %s" % (type(self).__name__, self.title or self.slug)


class Product(BaseSeoModel, ModelWithDescription):
    product_type = models.ForeignKey("products.ProductClass", on_delete=models.PROTECT, related_name="products")
    title = models.CharField(max_length=250, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, auto_created="title", db_index=True)
    is_public = models.BooleanField(default=True)
    attributes = models.ManyToManyField("products.ProductAttribute", through="products.ProductAttributeValue")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)


    class Meta:
        app_label = "products"
        ordering = ("-updated_at",)


    def __str__(self):
        return self.title or self.slug

    def __repr__(self):
        return "<%s> obj %s" % (type(self).__name__, self.title or self.slug)


class ProductAttribute(models.Model):
    product_class = models.ForeignKey(
        "products.ProductClass",
        on_delete=models.PROTECT,
        related_name="attributes",
        blank=True,
        null=True,
        db_index=True,
    )

    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=128, unique=True)
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE_CHOICE, default=VALUE_TYPE_CHOICE[0][0])
    require = models.BooleanField(default=False)


    class Meta:
        app_label = "products"
        unique_together = (("product_class", "slug"),)


    def __str__(self):
        return self.name or self.slug


class ProductAttributeValue(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey("products.ProductAttribute", on_delete=models.CASCADE)
    value = DynamicValueField()


    class Meta:
        app_label = "products"
        unique_together = (("product", "attribute"),)


    def __str__(self):
        return self.attribute.name

    _default_representation = "<No Display>"


    @property
    def data_type(self):
        return self.attribute.value_type
