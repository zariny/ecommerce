from django.db import models
from utils.models import DatedModel, ModelWithMetadata
from uuid import uuid4


class Order(DatedModel, ModelWithMetadata):
    ORDER_STATUS_PIPELINE = {
        'Pending': ('Being processed', 'Cancelled',),
        'Being processed': ('Complete', 'Cancelled',),
        'Cancelled': (),
        'Complete': (),
    }
    user = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True, blank=True)
    shipping_code = models.UUIDField(default=uuid4, editable=False)
    status = models.CharField(max_length=120)
    date_placed = models.DateTimeField(db_index=True)
    email = models.EmailField(verbose_name="Guest email address", blank=True, null=True)
    currency = models.CharField(max_length=12)
    total_incl_tax = models.DecimalField("Order total (include tax)", decimal_places=2, max_digits=12)
    total_excl_tax = models.DecimalField("Order total (exclude tax)", decimal_places=2, max_digits=12)
    shipping_incl_tax = models.DecimalField(
        "Shipping charge (include tax)",
        decimal_places=2,
        max_digits=12,
        default=0
    )
    shipping_excl_tax = models.DecimalField(
        "Shipping charge (exclude tax)",
        decimal_places=2,
        max_digits=12,
        default=0
    )
    shipping_method = models.CharField(max_length=128, blank=True)


class OrderLine(DatedModel):
    order = models.ForeignKey("order.order", on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("products.Product", on_delete=models.SET_NULL, null=True)
    stockrecord = models.ForeignKey("inventory.StockRecord", on_delete=models.CASCADE, related_name="order_lines")
    title = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=255, blank=True)
    line_price_incl_tax = models.DecimalField("Price (include tax)", decimal_places=2, max_digits=12)
    line_price_excl_tax = models.DecimalField("Price (exclude tax)", decimal_places=2, max_digits=12)
    line_price_before_discounts_incl_tax = models.DecimalField(
        "Price before discounts (include tax)",
        decimal_places=2,
        max_digits=12
    )
    line_price_before_discounts_excl_tax = models.DecimalField(
        "Price before discounts (exclude tax)",
        decimal_places=2,
        max_digits=12
    )
    unit_price_incl_tax = models.DecimalField(
        "Unit Price (include tax)",
        decimal_places=2,
        max_digits=12,
        blank=True,
        null=True
    )
    unit_price_excl_tax = models.DecimalField(
        "Unit Price (exclude tax)",
        decimal_places=2,
        max_digits=12,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title or self.product.title
