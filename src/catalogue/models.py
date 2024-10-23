from django.db import models
from src.core.models import BaseSeoModel, ModelWithMetadata
from treebeard.mp_tree import MP_Node


class Category(MP_Node, BaseSeoModel, ModelWithMetadata):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, auto_created="name", editable=False, allow_unicode=True)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    background = models.ImageField(upload_to="category-background", blank=True, null=True)
    background_caption = models.CharField(max_length=128, blank=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.slug or self.name

    def __repr__(self):
        return "<%s object> %s" % (self.__class__.__name__, str(self))
