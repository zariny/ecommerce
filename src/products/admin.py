from django.contrib import admin
from . import models
from .forms import ProductAttributeValueAdminForm
from core.admin import AbstractPieChartModelAdmin


class IsPublicFilter(admin.SimpleListFilter):
    title = "Is Public Product"
    parameter_name = "public"

    def lookups(self, request, model_admin):
        return [
            ("yes", "public"),
            ("no", "not public")
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(is_public=True)
        elif self.value() == "no":
            return queryset.filter(is_public=False)


class IsRequireFilter(admin.SimpleListFilter):
    title = "Is Require Attribute"
    parameter_name = "require"

    def lookups(self, request, model_admin):
        return [
            ("yes", "required"),
            ("no", "not required")
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(require=True)
        elif self.value() == "no":
            return queryset.filter(require=False)


class ProductAttributeValueInline(admin.TabularInline):
    model = models.ProductAttributeValue
    form = ProductAttributeValueAdminForm
    extra = 1


class ProductAttributeInline(admin.TabularInline):
    model = models.ProductAttribute
    extra = 1


class ProductClassRelationInline(admin.TabularInline):
    model = models.ProductClassRelation
    fk_name = "subclass"
    extra = 1


@admin.register(models.Product)
class ProductAdmin(AbstractPieChartModelAdmin):
    list_display = ("title", "is_public", "updated_at")
    search_fields = ("title",)
    list_filter = (IsPublicFilter,)
    inlines = (ProductAttributeValueInline,)


@admin.register(models.ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "data_type", "product")
    form = ProductAttributeValueAdminForm


@admin.register(models.ProductAttribute)
class ProductAttributeAdmin(AbstractPieChartModelAdmin):
    change_list_template = "core/pie_chart.html"
    list_display = ("name", "value_type", "require")
    search_fields = ("name", "slug")
    list_filter = (IsRequireFilter,)


@admin.register(models.ProductClass)
class ProductClassAdmin(admin.ModelAdmin):
    list_display = ("title", "abstract", "require_shipping", "track_stock")
    inlines = (ProductClassRelationInline, ProductAttributeInline,)


admin.site.register(models.ProductClassRelation)
admin.site.register(models.ProductTranslate)
admin.site.register(models.ProductAttributeTranslate)
admin.site.register(models.ProductAttributeValueTranslate)
