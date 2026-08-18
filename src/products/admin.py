from django.contrib import admin

from catalogue.models import ProductCategory

from . import models


class IsPublicFilter(admin.SimpleListFilter):
    title = "Is Public Product"
    parameter_name = "public"

    def lookups(self, request, model_admin):
        return [("yes", "public"), ("no", "not public")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(is_public=True)
        elif self.value() == "no":
            return queryset.filter(is_public=False)


class IsRequireFilter(admin.SimpleListFilter):
    title = "Is Require Attribute"
    parameter_name = "require"

    def lookups(self, request, model_admin):
        return [("yes", "required"), ("no", "not required")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(require=True)
        elif self.value() == "no":
            return queryset.filter(require=False)


class IsAbstraction(admin.SimpleListFilter):
    title = "Is Abstract Class"
    parameter_name = "abstract"

    def lookups(self, request, model_admin):
        return [("yes", "abstract"), ("no", "not abstract")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(abstract=True)
        elif self.value() == "no":
            return queryset.filter(abstract=False)


class IsRequiredShipping(admin.SimpleListFilter):
    title = "Is Required Shipping"
    parameter_name = "required-shipping"

    def lookups(self, request, model_admin):
        return [("yes", "required"), ("no", "not required")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(require_shipping=True)
        elif self.value() == "no":
            return queryset.filter(require_shipping=False)


class ProductAttributeInline(admin.TabularInline):
    model = models.Attribute.product_class.through
    extra = 1


class ParentProductClassInline(admin.TabularInline):
    model = models.ProductClassEdge
    fk_name = "child"
    extra = 1


class ProductCategoryInline(admin.StackedInline):
    model = ProductCategory
    fk_name = "product"
    extra = 1


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "is_public", "updated_at")
    search_fields = ("title",)
    list_filter = (IsPublicFilter,)
    inlines = (ProductCategoryInline,)


@admin.register(models.AttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "data_type")


@admin.register(models.Attribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "input_type", "value_required")
    search_fields = ("name", "slug")
    list_filter = (IsRequireFilter,)
    # filter_horizontal = ("product_class",)


@admin.register(models.ProductClass)
class ProductClassAdmin(admin.ModelAdmin):
    list_display = ("title", "abstract", "require_shipping", "track_stock")
    inlines = (ParentProductClassInline, ProductAttributeInline)
    list_filter = (
        IsAbstraction,
        IsRequiredShipping,
    )


@admin.register(models.ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ("product__title", "image", "published")
    autocomplete_fields = ("product",)


admin.site.register(models.ProductClassEdge)
admin.site.register(models.ProductTranslation)
admin.site.register(models.AttributeTranslation)
admin.site.register(models.AttributeValueTranslation)
