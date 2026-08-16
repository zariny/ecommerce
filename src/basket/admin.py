from django.contrib import admin

from . import models


@admin.register(models.Basket)
class BasketAdmin(admin.ModelAdmin):
    raw_id_fields = ("owner",)
    search_fields = ("pk", "token")


@admin.register(models.Line)
class LineAdmin(admin.ModelAdmin):
    raw_id_fields = ("product",)
    autocomplete_fields = ("basket", "stockrecord")
