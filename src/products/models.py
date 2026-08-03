from django.core.exceptions import ValidationError
from django.db import models

from utils.models import (
    BaseSeoModel,
    ModelWithDescription,
    ModelWithMetadata,
    SortableModel,
    TranslationModel,
)

from . import managers
from .attr_container import ProductAttributeContainer
from .fields import DynamicValueField
from .utils import VALUE_TYPE_CHOICE


class ProductClass(ModelWithMetadata):
    """
    Each instance of ProductClass can have multiple inheritances from other instances and
     inherit attributes and options from its ancestor classes.
    """

    title = models.CharField(max_length=250, db_index=True)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        auto_created="title",
        db_index=True,
    )
    require_shipping = models.BooleanField(default=True)
    track_stock = models.BooleanField(default=True)
    abstract = models.BooleanField(
        default=False
    )  # If True, this product class cannot have any product
    parents = models.ManyToManyField(
        "self",
        symmetrical=False,
        through="products.ProductClassEdge",
        through_fields=("child", "parent"),
        related_name="children",
        blank=True,
    )

    objects = managers.ProductClassManager()

    class Meta:
        app_label = "products"
        verbose_name_plural = "product classes"

    def __str__(self):
        return self.title or self.slug

    def __repr__(self):
        return f"<{type(self).__name__}> obj {self.title or self.slug}"

    def get_ancestors(self, include_self=False):
        rows = ProductClass.objects.get_ancestor_ids(self.pk)
        ordered_ids = [row["parent_id"] for row in rows]
        if include_self:
            ordered_ids = [self.pk] + ordered_ids
        preserved = models.Case(
            *[models.When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)]
        )
        return ProductClass.objects.filter(pk__in=ordered_ids).order_by(preserved)

    def get_descendants(self, include_self=False):
        rows = ProductClass.objects.get_descendant_ids(self.pk)
        ordered_ids = [row["child_id"] for row in rows]
        if include_self:
            ordered_ids = [self.pk] + ordered_ids
        preserved = models.Case(
            *[models.When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)]
        )
        return ProductClass.objects.filter(pk__in=ordered_ids).order_by(preserved)

    def get_attributes(self, **filters):
        attributes = self.attributes.model.objects.filter(
            product_class__in=self.get_ancestors(include_self=True), **filters
        ).distinct()
        return attributes


class ProductClassEdge(models.Model):
    """
    Represents a directed edge between two ProductClass nodes.

    This model implements an adjacency list representation of a
    Directed Acyclic Graph (DAG).
    """

    parent = models.ForeignKey(
        "products.ProductClass",
        on_delete=models.CASCADE,
        related_name="outgoing_edges",
        help_text="Parent class that this class inherits from.",
    )
    child = models.ForeignKey(
        "products.ProductClass",
        on_delete=models.CASCADE,
        related_name="incoming_edges",
        help_text="The class receiving inheritance.",
    )

    class Meta:
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["parent", "child"],
                name="unique_product_class_edge",
            ),
            models.CheckConstraint(
                condition=~models.Q(parent=models.F("child")),
                name="prevent_self_edge",
            ),
        ]
        app_label = "products"

    def __str__(self):
        return f"{self.child} --> {self.parent}"

    def clean(self):
        super().clean()
        self.validate_edge(parent_id=self.parent_id, child_id=self.child_id)

    @classmethod
    def validate_edge(cls, parent_id, child_id):
        """
        Validates ProductClass DAG constraints.
        """
        if parent_id == child_id:
            raise ValidationError("A ProductClass cannot inherit from itself.")
        if ProductClass.objects.check_cycle(parent_id, child_id):
            raise ValidationError("This relation creates a cycle.")


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
    attributes = models.ManyToManyField(
        "products.ProductAttribute", through="products.ProductAttributeValue"
    )
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


class ProductAttribute(models.Model):
    product_class = models.ManyToManyField(
        "products.ProductClass", related_name="attributes", blank=True
    )
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=128, unique=True)
    value_type = models.CharField(
        max_length=20, choices=VALUE_TYPE_CHOICE, default=VALUE_TYPE_CHOICE[0][0]
    )
    require = models.BooleanField(default=False)

    class Meta:
        app_label = "products"

    def __str__(self):
        return self.name or self.slug


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="attribute_values"
    )
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


class ProductMedia(ModelWithMetadata, SortableModel):
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="medias"
    )
    image = models.ImageField(upload_to="products", blank=True, null=True)
    caption = models.CharField(max_length=250, blank=True)
    published = models.BooleanField(default=False)

    class Meta(SortableModel.Meta):
        app_label = "products"


class ProductTranslate(TranslationModel):
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


class ProductAttributeTranslate(TranslationModel):
    attribute = models.ForeignKey(
        "products.ProductAttribute",
        on_delete=models.CASCADE,
        related_name="translations",
    )
    name = models.CharField(max_length=250)

    class Meta:
        indexes = (models.Index(fields=["attribute"]),)
        app_label = "products"
        unique_together = (("language_code", "attribute"),)
        verbose_name_plural = "translation of product attributes"

    def __str__(self):
        return f"{self.attribute.name} - {self.name or self._default_presentation}"


class ProductAttributeValueTranslate(TranslationModel):
    attribute_value = models.ForeignKey(
        "products.ProductAttributeValue",
        on_delete=models.CASCADE,
        related_name="translations",
    )
    value = models.TextField(blank=True)

    class Meta:
        indexes = (models.Index(fields=["attribute_value"]),)
        app_label = "products"
        unique_together = (("language_code", "attribute_value"),)
        verbose_name_plural = "translation of product attribute value"

    def __str__(self):
        return f"{self.attribute_value.attribute.name} - {self.value or self._default_presentation}"
