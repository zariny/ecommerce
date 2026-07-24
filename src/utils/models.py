from django.db import models
from django.conf import settings
from django_choices_field import TextChoicesField
from utils.languages import Language


class BaseSeoModel(models.Model):
    """Provides common SEO metadata fields."""

    meta_title = models.CharField(
        max_length=70,
        blank=True,
        null=True,
        help_text="SEO title for the page.",
    )
    meta_description = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="SEO meta description.",
    )

    class Meta:
        abstract = True


class SortableModel(models.Model):
    """Adds a field for custom ordering."""

    sort_order = models.IntegerField(
        db_index=True,
        null=True,
        help_text="Controls the display order.",
    )

    class Meta:
        ordering = ("-sort_order",)
        abstract = True


class BaseTranslateModel(models.Model):
    """Stores the language of a translated record."""

    language_code = TextChoicesField(
        choices_enum=Language,
        default=settings.LANGUAGE_CODE,
        help_text="Language of this translation.",
    )

    _default_presentation = "Not Translated"

    class Meta:
        abstract = True

    def __str__(self):
        return self._default_presentation


class SeoModel(BaseSeoModel):
    """Adds a unique SEO-friendly slug."""

    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        editable=False,
        help_text="Unique URL slug.",
    )

    class Meta:
        abstract = True


class ModelWithMetadata(models.Model):
    """Stores arbitrary structured metadata."""

    metadata = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Additional structured metadata.",
    )

    class Meta:
        abstract = True


class ModelWithDescription(ModelWithMetadata):
    """Adds a free-form description."""

    description = models.TextField(
        blank=True,
        help_text="Detailed description.",
    )

    class Meta:
        abstract = True


class TranslationModel(BaseSeoModel, BaseTranslateModel):
    """Base model for translated content."""

    class Meta:
        abstract = True


class DatedModel(models.Model):
    """Tracks creation and last update timestamps."""

    date_created = models.DateTimeField(
        "Date created",
        auto_now_add=True,
        help_text="Creation timestamp.",
    )
    date_updated = models.DateTimeField(
        "Date updated",
        auto_now=True,
        db_index=True,
        help_text="Last update timestamp.",
    )

    class Meta:
        abstract = True
