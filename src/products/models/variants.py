from django.db import models

from utils.models import ModelWithMetadata, SortableModel, TranslationModel


class ProductVariant(SortableModel, ModelWithMetadata):
    sku = models.CharField(max_length=255, unique=True, null=True, blank=True)
    """
    NOTE SKU: A stock keeping unit,
    Each SKU is unique to a product or product variation and is created by the retailer, not the manufacturer
    sku = TSHIRT-RED-M
    """

    name = models.CharField(max_length=255, blank=True)
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="variants"
    )
    track_inventory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ("sort_order", "sku")


class ProductVariantTranslation(TranslationModel):
    variant = models.ForeignKey(
        "products.ProductVariant", on_delete=models.CASCADE, related_name="translations"
    )
    name = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = (("name", "language_code"),)

    def get_translated_object_id(self):
        return "ProductVariant", self.product_variant_id


class AssignedVariantAttributeValue(SortableModel):
    value = models.ForeignKey(
        "products.AttributeValue",
        on_delete=models.CASCADE,
        related_name="variantvalueassignment",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name="attributevalues",
        null=True,
        blank=True,
    )
    assignment = models.ForeignKey(
        "products.AssignedVariantAttribute",
        on_delete=models.CASCADE,
        related_name="variantvalueassignment",
    )

    class Meta:
        unique_together = (("value", "assignment"),)
        ordering = ("sort_order", "pk")


class AssignedVariantAttribute(models.Model):
    """Associate a product type attribute and selected values to a given variant."""

    variant = models.ForeignKey(
        "products.ProductVariant", related_name="attributes", on_delete=models.CASCADE
    )
    assignment = models.ForeignKey(
        "products.AttributeVariant",
        on_delete=models.CASCADE,
        related_name="variantassignments",
    )
    values = models.ManyToManyField(
        "products.AttributeValue",
        blank=True,
        related_name="variantassignments",
        through=AssignedVariantAttributeValue,
    )

    class Meta:
        unique_together = (("variant", "assignment"),)


class AttributeVariant(SortableModel):
    attribute = models.ForeignKey(
        "products.Attribute", related_name="attributevariant", on_delete=models.CASCADE
    )
    product_type = models.ForeignKey(
        "products.ProductClass",
        related_name="attributevariant",
        on_delete=models.CASCADE,
    )
    assigned_variants = models.ManyToManyField(
        "products.ProductVariant",
        blank=True,
        through=AssignedVariantAttribute,
        through_fields=("assignment", "variant"),
        related_name="attributesrelated",
    )
    variant_selection = models.BooleanField(default=False)

    class Meta:
        unique_together = (("attribute", "product_type"),)
        ordering = ("sort_order", "pk")
