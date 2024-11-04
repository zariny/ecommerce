from django.db import models
from src.core.models import BaseSeoModel, ModelWithMetadata, TranslationModel
from treebeard.mp_tree import MP_Node


class Category(MP_Node, BaseSeoModel, ModelWithMetadata):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, auto_created="name", allow_unicode=True)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    background = models.ImageField(upload_to="category-background", blank=True, null=True)
    background_caption = models.CharField(max_length=128, blank=True)

    is_public = models.BooleanField(default=True)
    ancestors_are_public = models.BooleanField(default=True)

    class Meta:
        indexes = (
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["path"]),
            models.Index(fields=["depth"]),
        )
        app_label = "catalogue"
        ordering = ("path",)
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name or self.slug

    def __repr__(self):
        return "<%s obj> %s" % (type(self).__name__, self.name)

    _full_name_seperator = " > "

    @property
    def full_name(self):
        names = [category.name for category in self.get_ancestors()]
        names.append(self.name)
        return self._full_name_seperator.join(names)

    _full_slug_seperator = "/"

    @property
    def full_slug(self):
        slugs = [category.slug for category in self.get_ancestors()]
        slugs.append(self.slug)
        return self._full_slug_seperator.join(slugs)

    def has_children(self):
        return self.numchild > 0


class CategoryTranslation(TranslationModel):
    category = models.ForeignKey("catalogue.Category", on_delete=models.CASCADE, related_name="translations")
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.category.name, self.name or self._default_presentation)

    class Meta:
        indexes = (
            models.Index(fields=["category"]),
            )
        app_label = "catalogue"
        unique_together = (("language_code", "category"),)
