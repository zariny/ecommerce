from django.contrib import admin
from core.admin import AbstractPieChartModelAdmin
from . import models


@admin.register(models.Basket)
class BasketAdmin(AbstractPieChartModelAdmin):
    raw_id_fields = ("owner",)
    search_fields = ("pk", "token")


@admin.register(models.Line)
class LineAdmin(AbstractPieChartModelAdmin):
    raw_id_fields = ("product",)
    autocomplete_fields = ("basket", "stockrecord")
