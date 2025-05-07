from django.db import models
from core.models import DatedModel
from core.utils import currencies
from uuid import uuid4


class Basket(DatedModel):
    owner = models.ForeignKey("account.User", on_delete=models.CASCADE, related_name="carts", null=True)
    token = models.UUIDField(default=uuid4, editable=False)
    OPEN, MERGED, SAVED, FROZEN, SUBMITTED = (
        "Open",
        "Merged",
        "Saved",
        "Frozen",
        "Submitted",
    )
    STATUS_CHOICES = (
        (OPEN, "Open - currently active"),
        (MERGED, "Merged - superceded by another basket"),
        (SAVED, "Saved - for items to be purchased later"),
        (FROZEN, "Frozen - the basket cannot be modified"),
        (SUBMITTED, "Submitted - has been ordered at the checkout"),
    )
    status = models.CharField(max_length=128, default=OPEN, choices=STATUS_CHOICES)


class Line(DatedModel):
    basket = models.ForeignKey("basket.Basket", on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    stockrecord = models.ForeignKey("inventory.StockRecord", on_delete=models.CASCADE, related_name="basket_lines")
    quantity = models.PositiveIntegerField(default=1)
    price_currency = models.CharField(max_length=4 ,choices=currencies, default=currencies[0][0])
    price_excl_tax = models.DecimalField(
        "Price excluding tax",
        decimal_places=2,
        max_digits=12,
        null=True
    )
    price_incl_tax = models.DecimalField("Price includes tax", decimal_places=2, max_digits=12, null=True)
    tax_code = models.CharField(verbose_name="VAT rate code", max_length=64, blank=True, null=True)

    class Meta:
        ordering = ("date_created", "pk")
