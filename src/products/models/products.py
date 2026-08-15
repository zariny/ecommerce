from django.core.exceptions import ValidationError
from django.db import models

from utils.models import (
    BaseSeoModel,
    ModelWithDescription,
    ModelWithMetadata,
    SortableModel,
    TranslationModel,
)

from .. import managers
from ..attr_container import ProductAttributeContainer


class Product(BaseSeoModel, ModelWithDescription):
    product_type = models.ForeignKey(
        "products.ProductClass", on_delete=models.PROTECT, related_name="products"
    )
    title = models.CharField(max_length=250, db_index=True)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        auto_created="title",
        db_index=True,
    )
    is_public = models.BooleanField(default=True)
    categories = models.ManyToManyField(
        "catalogue.Category",
        through="catalogue.ProductCategory",
        related_name="products",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = managers.ProductManager()

    class Meta:
        app_label = "products"
        ordering = ("-updated_at",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attr = ProductAttributeContainer(self)

    def __str__(self):
        return self.title or self.slug

    def __repr__(self):
        return f"<{type(self).__name__}> obj {self.title or self.slug}"

    def clean(self):
        super().clean()
        if self.product_type_id and self.product_type.abstract:
            raise ValidationError(
                {
                    "product_type": f"Abstract product type {self.product_type} can not have any product."
                }
            )

    def refresh_from_db(self, using=None, fields=None, from_queryset=None):
        result = super().refresh_from_db(using, fields, from_queryset)
        self.attr.invalidate()
        return result


class ProductMedia(ModelWithMetadata, SortableModel):
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="medias"
    )
    image = models.ImageField(upload_to="products", blank=True, null=True)
    caption = models.CharField(max_length=250, blank=True)
    published = models.BooleanField(default=False)

    class Meta(SortableModel.Meta):
        app_label = "products"


class ProductTranslation(TranslationModel):
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="translations"
    )
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)

    class Meta:
        indexes = (models.Index(fields=["product"]),)
        app_label = "products"
        unique_together = (("language_code", "product"),)
        verbose_name_plural = "translation of products"

    def __str__(self):
        return f"{self.product.title} - {self.title or self._default_presentation}"
