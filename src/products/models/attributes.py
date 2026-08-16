from django.db import models

from utils.models import ModelWithMetadata, SortableModel, TranslationModel

from ..units import MeasurementUnits


class AttributeInputType(models.TextChoices):
    """Defines how an attribute value is entered and stored."""

    DROPDOWN = "dropdown"
    """Allows selecting a single value from a predefined list."""

    MULTISELECT = "multiselect"
    """Allows selecting multiple values from a predefined list."""

    FILE = "file"
    """Allows uploading or selecting a file as the attribute value."""

    REFERENCE = "reference"
    """Allows selecting one or more objects referenced by the attribute."""

    SINGLE_REFERENCE = "single-reference"
    """Allows selecting a single object referenced by the attribute."""

    NUMERIC = "numeric"
    """Stores a numeric value, optionally with a unit of measurement."""

    RICH_TEXT = "rich-text"
    """Stores formatted text that may contain rich content."""

    PLAIN_TEXT = "plain-text"
    """Stores unformatted plain text."""

    SWATCH = "swatch"
    """Allows selecting a value represented by a visual swatch, such as a color."""

    BOOLEAN = "boolean"
    """Stores a true or false value."""

    DATE = "date"
    """Stores a calendar date without a time component."""

    DATE_TIME = "date-time"
    """Stores a date and time value."""


class Attribute(ModelWithMetadata):
    product_class = models.ManyToManyField(
        "products.ProductClass",
        through="products.AttributeProductClass",
        related_name="attributes",
        blank=True,
    )
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=128, unique=True)
    input_type = models.CharField(
        max_length=20, choices=AttributeInputType, default=AttributeInputType.DROPDOWN
    )
    unit = models.CharField(
        max_length=100, choices=MeasurementUnits, blank=True, null=True
    )
    value_required = models.BooleanField(default=False, blank=True)
    variant_only = models.BooleanField(default=False, blank=True)

    class Meta:
        app_label = "products"

    def __str__(self):
        return self.name or self.slug

    def has_values(self):
        return self.values.exists()


class AttributeTranslation(TranslationModel):
    attribute = models.ForeignKey(
        "products.Attribute",
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


class AttributeProductClass(SortableModel):
    attribute = models.ForeignKey(
        "products.Attribute",
        on_delete=models.CASCADE,
        related_name="attributeproductclass",
    )
    product_class = models.ForeignKey(
        "products.ProductClass",
        on_delete=models.CASCADE,
        related_name="attributeproductclass",
    )

    class Meta:
        unique_together = (("attribute", "product_class"),)
        ordering = ("sort_order", "pk")
