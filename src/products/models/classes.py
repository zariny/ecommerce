from django.core.exceptions import ValidationError
from django.db import models

from utils.models import ModelWithMetadata

from .. import managers


class ProductClass(ModelWithMetadata):
    """
    Each instance of ProductClass can have multiple inheritances from other instances and
     inherit attributes and options from its ancestor classes.
    """

    title = models.CharField(max_length=250, db_index=True)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        auto_created="title",
        db_index=True,
    )
    require_shipping = models.BooleanField(default=True)
    track_stock = models.BooleanField(default=True)
    abstract = models.BooleanField(
        default=False
    )  # If True, this product class cannot have any product
    parents = models.ManyToManyField(
        "self",
        symmetrical=False,
        through="products.ProductClassEdge",
        through_fields=("child", "parent"),
        related_name="children",
        blank=True,
    )

    objects = managers.ProductClassManager()

    class Meta:
        app_label = "products"
        verbose_name_plural = "product classes"

    def __str__(self):
        return self.title or self.slug

    def __repr__(self):
        return f"<{type(self).__name__}> obj {self.title or self.slug}"

    def get_ancestors(self, include_self=False):
        rows = ProductClass.objects.get_ancestor_ids(self.pk)
        ordered_ids = [row["parent_id"] for row in rows]
        if include_self:
            ordered_ids = [self.pk] + ordered_ids
        preserved = models.Case(
            *[models.When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)]
        )
        return ProductClass.objects.filter(pk__in=ordered_ids).order_by(preserved)

    def get_descendants(self, include_self=False):
        rows = ProductClass.objects.get_descendant_ids(self.pk)
        ordered_ids = [row["child_id"] for row in rows]
        if include_self:
            ordered_ids = [self.pk] + ordered_ids
        preserved = models.Case(
            *[models.When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)]
        )
        return ProductClass.objects.filter(pk__in=ordered_ids).order_by(preserved)

    def get_attributes(self, **filters):
        attributes = self.attributes.model.objects.filter(
            product_class__in=self.get_ancestors(include_self=True), **filters
        ).distinct()
        return attributes


class ProductClassEdge(models.Model):
    """
    Represents a directed edge between two ProductClass nodes.

    This model implements an adjacency list representation of a
    Directed Acyclic Graph (DAG).
    """

    parent = models.ForeignKey(
        "products.ProductClass",
        on_delete=models.CASCADE,
        related_name="outgoing_edges",
        help_text="Parent class that this class inherits from.",
    )
    child = models.ForeignKey(
        "products.ProductClass",
        on_delete=models.CASCADE,
        related_name="incoming_edges",
        help_text="The class receiving inheritance.",
    )

    class Meta:
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["parent", "child"],
                name="unique_product_class_edge",
            ),
            models.CheckConstraint(
                condition=~models.Q(parent=models.F("child")),
                name="prevent_self_edge",
            ),
        ]
        app_label = "products"

    def __str__(self):
        return f"{self.child} --> {self.parent}"

    def clean(self):
        super().clean()
        self.validate_edge(parent_id=self.parent_id, child_id=self.child_id)

    @classmethod
    def validate_edge(cls, parent_id, child_id):
        """
        Validates ProductClass DAG constraints.
        """
        if parent_id == child_id:
            raise ValidationError("A ProductClass cannot inherit from itself.")
        if ProductClass.objects.check_cycle(parent_id, child_id):
            raise ValidationError("This relation creates a cycle.")
