from django.contrib import admin

from . import models


@admin.register(models.StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    autocomplete_fields = ("product", )
    search_fields = ("product__title", "pk")
