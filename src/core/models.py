from django.db import models


class BaseSeoModel(models.Model):
    meta_title = models.CharField(max_length=70, blank=True, null=True)
    meta_description = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        abstract = True


class BaseTranslateModel(models.Model):
    language_code = models.CharField(max_length=35)

    _default_presentation = "Not Translated"

    class Meta:
        abstract = True


class SeoModel(BaseSeoModel):
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, editable=False)

    class Meta:
        abstract = True


class ModelWithMetadata(models.Model):
    metadata = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        abstract = True


class TranslationModel(BaseSeoModel, BaseTranslateModel):
    class Meta:
        abstract = True
