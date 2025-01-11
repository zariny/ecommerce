from django.db import models
from django.core.exceptions import ValidationError
from django.core.cache import cache
from core.models import ModelWithDescription, BaseSeoModel, ModelWithMetadata, TranslationModel
from .utils import VALUE_TYPE_CHOICE
from .fields import DynamicValueField
from .validation import validate_no_cycles
from .exceptions import CycleInheritanceError


class ProductClass(ModelWithMetadata):
    """
        Each instance of ProductClass can have multiple inheritances from other instances and
         inherit attributes and options from its ancestor classes.
    """
    title = models.CharField(max_length=250, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, auto_created="title", db_index=True)
    require_shipping = models.BooleanField(default=True)
    track_stock = models.BooleanField(default=True)
    abstract = models.BooleanField(default=False) # If True, this product class cannot have any product
    bases = models.ManyToManyField(
        "self",
        symmetrical=False,
        through="products.ProductClassRelation",
        related_name="subclasses"
    )

    class Meta:
        app_label = "products"
        verbose_name_plural = "product classes"

    def __str__(self):
        return self.title or self.slug

    def __repr__(self):
        return "<%s> obj %s" % (type(self).__name__, self.title or self.slug)


class ProductClassRelation(models.Model):
    subclass = models.ForeignKey("products.ProductClass", on_delete=models.CASCADE, related_name="base_relations")
    base = models.ForeignKey("products.ProductClass", on_delete=models.CASCADE, related_name="sub_relations")

    class Meta:
        unique_together = (("base", "subclass"),)
        app_label = "products"

    def __str__(self):
        return "%s inherits from %s" % (self.subclass, self.base)

    def clean(self):
        super().clean()
        if self.base == self.subclass:
            raise ValidationError("Self-inheritance is not allowed.")

        self._check_reverse_relation()

        try:
            validate_no_cycles(base_product_kls=self.base, sub_product_kls=self.subclass)
        except CycleInheritanceError as e:
            raise ValidationError(message=e.message)

    def _check_reverse_relation(self):
        # Any two instances of the ProductClass should have only one relationship with each other.
        if self.base.pk and self.subclass.pk:
            if type(self)._default_manager.filter(base=self.subclass, subclass=self.base).exists():
                raise ValidationError("The inverse of this relationship has already been stored.")


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

    def clean(self):
        super().clean()
        if self.product_type.abstract:
            raise ValidationError("Abstract product type %s can not have any product." % self.product_type)


class ProductAttribute(models.Model):
    product_class = models.ManyToManyField("products.ProductClass", related_name="attributes", blank=True)
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=128, unique=True)
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE_CHOICE, default=VALUE_TYPE_CHOICE[0][0])
    require = models.BooleanField(default=False)

    class Meta:
        app_label = "products"

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


class ProductTranslate(TranslationModel):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="translations")
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)

    class Meta:
        indexes = (
            models.Index(fields=["product"]),
        )
        app_label = "products"
        unique_together = (("language_code", "product"),)
        verbose_name_plural = "translation of products"

    def __str__(self):
        return "%s - %s" % (self.product.title, self.title or self._default_presentation)


class ProductAttributeTranslate(TranslationModel):
    attribute = models.ForeignKey("products.ProductAttribute", on_delete=models.CASCADE, related_name="translations")
    name = models.CharField(max_length=250)

    class Meta:
        indexes = (
            models.Index(fields=["attribute"]),
        )
        app_label = "products"
        unique_together = (("language_code", "attribute"),)
        verbose_name_plural = "translation of product attributes"

    def __str__(self):
        return "%s - %s" % (self.attribute.name, self.name or self._default_presentation)


class ProductAttributeValueTranslate(TranslationModel):
    attribute_value = models.ForeignKey(
        "products.ProductAttributeValue",
        on_delete=models.CASCADE,
        related_name="translations"
    )
    value = models.TextField(blank=True)

    class Meta:
        indexes = (
            models.Index(fields=["attribute_value"]),
        )
        app_label = "products"
        unique_together = (("language_code", "attribute_value"),)
        verbose_name_plural = "translation of product attribute value"

    def __str__(self):
        return "%s - %s" % (self.attribute_value.attribute.name, self.value or self._default_presentation)
