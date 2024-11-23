from django.contrib import admin
from . import models


class AttributeValueAdmin(admin.TabularInline):
    model = models.ProductAttributeValue


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (AttributeValueAdmin,)
