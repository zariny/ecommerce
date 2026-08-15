from django.db import models

from utils.models import SortableModel, TranslationModel


class AssignedProductAttributeValue(SortableModel):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="attributevalues",
        null=False,
        blank=False,
    )
    value = models.ForeignKey(
        "products.AttributeValue",
        on_delete=models.CASCADE,
        related_name="attributevalues",
    )

    class Meta:
        unique_together = (("product", "value"),)


class AttributeValue(models.Model):
    label = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Human-readable label used to display the attribute value to users.",
    )
    attribute = models.ForeignKey(
        "products.Attribute", on_delete=models.CASCADE, related_name="values"
    )

    value = models.CharField(max_length=255, blank=True, null=True)
    rich_text = models.JSONField(
        blank=True, null=True
    )  # FIXME sanitize content before store on database
    plain_text = models.TextField(blank=True, null=True)
    boolean = models.BooleanField(blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    numeric = models.FloatField(blank=True, null=True)

    reference_product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="references",
        blank=True,
        null=True,
    )
    refreence_category = models.ForeignKey(
        "catalogue.Category",
        on_delete=models.CASCADE,
        related_name="references",
        blank=True,
        null=True,
    )

    class Meta:
        unique_together = (("label", "attribute"),)

    @property
    def data_type(self):
        return self.attribute.data_type


class AttributeValueTranslation(TranslationModel):
    attribute_value = models.ForeignKey(
        "products.AttributeValue",
        on_delete=models.CASCADE,
        related_name="translations",
    )
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True, null=True)
    rich_text = models.JSONField(
        blank=True, null=True
    )  # FIXME sanitize content before store on database

    plain_text = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        indexes = (models.Index(fields=["attribute_value"]),)
        unique_together = (("language_code", "attribute_value"),)
        verbose_name_plural = "translation of product attribute value"

    def __str__(self):
        return f"{self.attribute_value.attribute.name} - {self.value or self._default_presentation}"
