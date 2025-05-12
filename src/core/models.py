from django.db import models
from django.conf import settings


class BaseSeoModel(models.Model):
    meta_title = models.CharField(max_length=70, blank=True, null=True)
    meta_description = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        abstract = True


class SortableModel(models.Model):
    sort_order = models.IntegerField(db_index=True, null=True)

    class Meta:
        abstract = True


class BaseTranslateModel(models.Model):
    language_code = models.CharField(max_length=35, choices=settings.CORE_LANGUAGES, default=settings.LANGUAGE_CODE)

    _default_presentation = "Not Translated"

    class Meta:
        abstract = True


    def __str__(self):
        return self._default_presentation


class SeoModel(BaseSeoModel):
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, editable=False)

    class Meta:
        abstract = True


class ModelWithMetadata(models.Model):
    metadata = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        abstract = True


class ModelWithDescription(ModelWithMetadata):
    description = models.TextField(blank=True)

    class Meta:
        abstract = True


class TranslationModel(BaseSeoModel, BaseTranslateModel):

    class Meta:
        abstract = True


class DatedModel(models.Model):
    date_created = models.DateTimeField("Date created", auto_now_add=True)
    date_updated = models.DateTimeField("Date updated", auto_now=True, db_index=True)

    class Meta:
        abstract = True
