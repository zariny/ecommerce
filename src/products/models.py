from django.db import models
from src.core.models import SeoModel, ModelWithMetadata


class ProductType(ModelWithMetadata):
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


class Product(SeoModel, ModelWithMetadata):
    product_type = models.ForeignKey("products.Product_type", on_delete=models.PROTECT, related_name="products")
    title = models.CharField(max_length=250, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, auto_created="title", db_index=True)


    class Meta:
        app_label = "products"


    def __str__(self):
        return self.title or self.slug

    def __repr__(self):
        return "<%s> obj %s" % (type(self).__name__, self.title or self.slug)



class ProductAttribute(models.Model):
    product_type = models.ForeignKey(
        "products.ProductType",
        on_delete=models.PROTECT,
        related_name="attributes",
        blank=True,
        null=True,
        db_index=True,
    )
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=128, unique=True)
    value_type = ...








