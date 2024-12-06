from django.contrib import admin
from . import models
from .forms import ProductAttributeValueAdminForm


class ProductAttributeValueInline(admin.TabularInline):
    model = models.ProductAttributeValue
    form = ProductAttributeValueAdminForm
    extra = 1


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "is_public", "updated_at")
    search_fields = ("title",)
    inlines = (ProductAttributeValueInline,)


@admin.register(models.ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "data_type", "product")
    form = ProductAttributeValueAdminForm


@admin.register(models.ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "value_type", "require")
    search_fields = ("name", "slug")
