from typing import TYPE_CHECKING, Annotated, Optional, Self

import strawberry_django
from strawberry import auto, lazy, enum
from strawberry.relay import Node
from strawberry.types import Info

from utils.types import (
    BaseSeoModelType,
    ModelWithDescriptionType,
    ModelWithMetadataType,
    TranslationModelFilter,
    TranslationModelType,
    SortableModelType,
)
from utils.relay import CursorConnection

from .. import models

if TYPE_CHECKING:
    from catalogue.dashboard.types import CategoryType


#####
# FILTERS
#####


@strawberry_django.filter_type(models.ProductClass, lookups=True)
class ProductClassFilter:
    id: auto
    title: auto
    slug: auto
    require_shipping: auto
    track_stock: auto
    abstract: auto


@strawberry_django.filter_type(models.Product, lookups=True)
class ProductFilter:
    id: auto
    title: auto
    slug: auto
    is_public: auto
    created_at: auto
    updated_at: auto
    product_type: Optional[ProductClassFilter]


@strawberry_django.filter_type(models.Attribute, lookups=True)
class AttributeFilter:
    input_type: auto
    product_class: Optional[ProductClassFilter]
    variant_only: auto
    value_required: auto


@strawberry_django.filter_type(models.ProductVariant, lookups=True)
class ProductVariantFilter:
    sku: auto
    name: auto
    product: Optional[ProductFilter]
    track_inventory: auto
    created_at: auto
    updated_at: auto


#####
# TYPES
#####


@strawberry_django.type(models.ProductClass, filters=ProductClassFilter)
class ProductClassType(Node, ModelWithMetadataType):
    title: auto
    slug: auto
    require_shipping: auto
    track_stock: auto
    abstract: auto
    parents: list[Self]
    children: list[Self]
    products: CursorConnection["ProductType"] = strawberry_django.connection()
    attributes: CursorConnection["AttributeType"] = strawberry_django.connection()
    # TODO add a field for fetch all inherited attributes from ancestors

    @strawberry_django.field
    def ancestors(
        self, info: Info, filters: Optional["ProductClassFilter"] = None
    ) -> list[Self]:
        qs = self.get_ancestors()
        if filters:
            qs = strawberry_django.filters.apply(filters, qs, info)
        return qs

    @strawberry_django.field
    def descendants(
        self, info: Info, filters: Optional["ProductClassFilter"] = None
    ) -> list[Self]:
        qs = self.get_descendants()
        if filters:
            qs = strawberry_django.filters.apply(filters, qs, info)
        return qs

    @strawberry_django.field
    def variant_attributes(
        self,
        info: Info,
        root: models.ProductClass,
        filters: Optional["AttributeFilter"] = None,
    ) -> list["AttributeType"]:
        qs = models.Attribute.objects.filter(
            attributevariant__product_class=root
        ).distinct()
        if filters:
            qs = strawberry_django.filters.apply(filters, qs, info)
        return list(qs)


@strawberry_django.type(models.Product, filters=ProductFilter)
class ProductType(Node, BaseSeoModelType, ModelWithDescriptionType):
    title: auto
    slug: auto
    is_public: auto
    created_at: auto
    updated_at: auto
    categories: list[Annotated["CategoryType", lazy("catalogue.dashboard.types")]]
    translations: list["ProductTranslateType"]
    product_type: Optional["ProductClassType"]
    variants: CursorConnection["ProductVariantType"] = strawberry_django.connection()
    medias: CursorConnection["ProductMediaType"] = strawberry_django.connection()

    @strawberry_django.field
    def attributes(
        self,
        root: models.Product,
        info: Info,
        filters: Optional["AttributeFilter"] = None,
    ) -> list["ProductAttributeValueType"]:
        qs = root.attributevalues.select_related("value__attribute")
        if filters:
            attr_qs = strawberry_django.filters.apply(
                filters, models.Attribute.objects.all(), info
            )
            qs = qs.filter(value__attributes__in=attr_qs)
        return list(qs)


@strawberry_django.type(models.AssignedProductAttributeValue)
class ProductAttributeValueType(SortableModelType):
    @strawberry_django.field
    def attribute(self, root) -> "AttributeType":
        return root.value.attribute

    @strawberry_django.field
    def value(self, root) -> "AttributeValueType":
        return root.value


@strawberry_django.type(models.Attribute, filters=AttributeFilter)
class AttributeType(Node, ModelWithMetadataType):
    name: auto
    slug: auto
    input_type: auto
    value_required: auto
    variant_only: auto
    unit: auto
    translations: list["AttributeTranslationType"]


@strawberry_django.type(models.AttributeValue)
class AttributeValueType(Node):
    attribute: "AttributeType"
    label: auto
    translations: list["AttributeValueTranslationType"]
    value: auto
    rich_text: auto
    plain_text: auto
    boolean: auto
    date_time: auto
    numeric: auto

    reference_product: Optional["ProductType"]
    reference_variant: Optional["ProductVariantType"]
    reference_category: Optional[
        Annotated["CategoryType", lazy("catalogue.dashboard.types")]
    ]

    @strawberry_django.field
    def data_type(self, root) -> enum(models.AttributeInputType):  # type: ignore
        return root.data_type


@strawberry_django.type(models.ProductMedia)
class ProductMediaType(Node, ModelWithMetadataType, SortableModelType):
    product: Optional["ProductType"]
    image: auto
    caption: auto
    published: auto


@strawberry_django.type(models.AssignedVariantAttribute)
class VariantAttributeType:
    @strawberry_django.field
    def attribute(self, root: models.AssignedVariantAttribute) -> AttributeType:
        return root.assignment.attribute

    @strawberry_django.field
    def values(self, root: models.AssignedVariantAttribute) -> list[AttributeValueType]:
        return [
            vv.value for vv in root.variantvalueassignment.select_related("value").all()
        ]


@strawberry_django.type(models.ProductVariant, filters=ProductVariantFilter)
class ProductVariantType(Node, SortableModelType, ModelWithMetadataType):
    sku: auto
    name: auto
    track_inventory: auto
    created_at: auto
    updated_at: auto
    product: Optional["ProductType"]
    translations: list["ProductVariantTranslationType"]

    @strawberry_django.field
    def attributes(
        self,
        root: models.ProductVariant,
        info: Info,
        filters: Optional[AttributeFilter] = None,
    ) -> list[VariantAttributeType]:
        qs = root.attributes.select_related("assignment__attribute").prefetch_related(
            "variantvalueassignment__value"
        )
        if filters:
            attr_qs = strawberry_django.filters.apply(
                filters, models.Attribute.objects.all(), info
            )
            qs = qs.filter(assignment__attribute__in=attr_qs)

        return list(qs)


#####
# TRANSLATION TYPES
#####


@strawberry_django.type(
    models.ProductVariantTranslation, filters=TranslationModelFilter
)
class ProductVariantTranslationType(Node, TranslationModelType):
    name: auto
    variant: Optional["ProductVariantType"]


@strawberry_django.type(models.ProductTranslation, filters=TranslationModelFilter)
class ProductTranslateType(Node, TranslationModelType):
    title: auto
    description: auto
    product: Optional["ProductType"]


@strawberry_django.type(models.AttributeTranslation, filters=TranslationModelFilter)
class AttributeTranslationType(Node, TranslationModelType):
    name: auto
    attribute: Optional["AttributeType"]


@strawberry_django.type(
    models.AttributeValueTranslation, filters=TranslationModelFilter
)
class AttributeValueTranslationType(Node, TranslationModelType):
    label: auto
    value: auto
    rich_text: auto
    plain_text: auto
    attribute_value: Optional["AttributeValueType"]
