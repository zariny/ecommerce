from django.contrib import admin
from . import models
from . import forms


class ProductAttributeValueInline(admin.TabularInline):
    model = models.ProductAttributeValue
    form = forms.ProductAttributeValueForm
    extra = 1


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "is_public", "updated_at")
    inlines = (ProductAttributeValueInline,)


@admin.register(models.ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):

    list_display = ("attribute", "data_type", "product")

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj is not None:
            return forms.ProductAttributeValueForm
        return super().get_form(request, obj, change, **kwargs)


@admin.register(models.ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "value_type", "require")
