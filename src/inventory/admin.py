from django.contrib import admin
from utils.admin import AbstractPieChartModelAdmin
from . import models


@admin.register(models.StockRecord)
class StockRecordAdmin(AbstractPieChartModelAdmin):
    autocomplete_fields = ("product", )
    search_fields = ("product__title", "pk")
