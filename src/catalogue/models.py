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

    _full_name_seperator = '>'
    class Meta:
        app_label = "catalogue"
        ordering = ("path",)
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name or self.slug

    def __repr__(self):
        return "<%s object> %s" % (self.__class__.__name__, str(self.full_name))

    @property
    def full_name(self):
        names = [category.name for category in self.get_ancestors()]
        return self._full_name_seperator.join(names)

    def has_children(self):
        return self.get_num_children() > 0

    def get_num_children(self):
        return self.numchild().count()


class CategoryTranslation(TranslationModel):
    category = models.ForeignKey("catalogue.Category", on_delete=models.CASCADE, related_name="translations")
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        app_label = "catalogue"
        unique_together = (("language_code", "category"),)
