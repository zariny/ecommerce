from django.contrib import admin
from core.admin import AbstractPieChartModelAdmin
from . import models


@admin.register(models.Order)
class OrderAdmin(AbstractPieChartModelAdmin):
    autocomplete_fields = ("user",)
    readonly_fields = ("shipping_code", "date_updated", "date_created")
    fieldsets = (
        (None, {"fields": ("status", "metadata", )}),
        ("owner", {"fields": ("user", "email")}),
        ("fields", {"fields": ("currency", "total_incl_tax", "total_excl_tax")}),
        ("shipping", {
            "fields": (
            "shipping_code",
            "shipping_method",
            "date_placed",
            "shipping_incl_tax",
            "shipping_excl_tax")
        }),
        ("date", {"fields": ("date_created", "date_updated")})
    )
    ordering = ("-date_updated",)
    list_display = ("shipping_code", "status")
    search_fields = ("pk", "sshipping_code", "email")
    list_filter = ("date_placed", "status")


@admin.register(models.OrderLine)
class OrderLineAdmin(AbstractPieChartModelAdmin):
    autocomplete_fields = ("product",)
    raw_id_fields = ("order", "stockrecord")
    list_display = ("title", "quantity", "line_price_incl_tax")
