from django.db import models
from django.utils.text import slugify
from src.core.models import BaseSeoModel, ModelWithDescription, TranslationModel
from treebeard.mp_tree import MP_Node, MP_NodeQuerySet


class ReverseStartsWithLookup(models.lookups.StartsWith):
    """
    just like normal (startswith) lookup but performs a reverse "starts with" query,
     so that the left-hand side (lhs) and right-hand side (rhs) positions are swapped.

    This lookup behaves similarly to Django's built-in `StartsWith` lookup,
    but with the lhs and rhs reversed. It allows querying if a specified value
    (rhs) "starts with" the field's value (lhs) instead of the typical order.

    For example:
        - my_field__rstartswith = "prefix"
          will check if "prefix" starts with values in the field `my_field`.
    """

    def process_rhs(self, qn, connection):
        return super().process_lhs(qn, connection)

    def process_lhs(self, compiler, connection, lhs=None):
        if lhs is not None:
            raise Exception("Flipped process_lhs does not accept lhs argument")
        return super().process_rhs(compiler, connection)


models.Field.register_lookup(ReverseStartsWithLookup, "rstartswith")


class CategoryQuerySet(MP_NodeQuerySet):
    def browsable(self):
        return self.filter(is_public=True, ancestors_are_public=True)



class Category(MP_Node, BaseSeoModel, ModelWithDescription):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, auto_created="name", allow_unicode=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    background = models.ImageField(upload_to="category-background", blank=True, null=True)
    background_caption = models.CharField(max_length=128, blank=True)

    is_public = models.BooleanField(default=True)
    ancestors_are_public = models.BooleanField(default=True)

    objects = CategoryQuerySet.as_manager()

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
    def full_name(self) -> str:
        names = [category.name for category in self.get_ancestors()]
        names.append(self.name)
        return self._full_name_seperator.join(names)

    _full_slug_seperator = "/"

    @property
    def full_slug(self) -> str:
        slugs = [category.slug for category in self.get_ancestors()]
        slugs.append(self.slug)
        return self._full_slug_seperator.join(slugs)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def refresh_ancestors_are_public(self):
        """
            set correct value for (ancestors_are_public) field
             via check ancestor's (is_public) field for each subtree.

            - this method avoid run a new save for each updated object.
        """
        subquery = type(self)._default_manager.filter(
            is_public=False,
            path__rstartswith=models.OuterRef("path"),
            depth__lt=models.OuterRef("depth")
        )

        self.get_tree(self).update(
            ancestors_are_public=~models.Exists(subquery.values("pk"))
        )

        self.refresh_from_db()

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


class ProductCategory(models.Model):
    category = models.ForeignKey("catalogue.Category", on_delete=models.CASCADE, related_name="product")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="category")

    class Meta:
        app_label = "catalogue"
        unique_together = (("category", "product"),)
        ordering = ("product", "category")
        verbose_name = "Product category"
        verbose_name_plural = "Product categories"

    def __str__(self):
        return "%s is in the %s category" % (self.product, self.category)
