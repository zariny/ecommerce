from django.contrib import admin
from . import models
from . import forms


class AttributeValueAdmin(admin.TabularInline):
    model = models.ProductAttributeValue
    extra = 1


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (AttributeValueAdmin,)


@admin.register(models.ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):

    list_display = ("attribute", "data_type", "product",)

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj is not None:
            return forms.ProductAttributeValueChangeForm
        return super().get_form(request, obj, change, **kwargs)


admin.site.register(models.ProductAttribute)
admin.site.register(models.ProductClass)
