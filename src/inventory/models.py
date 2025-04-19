from django.db import models
from core.models import DatedModel
from core.utils import currencies


class StockRecord(DatedModel):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="stockrecords")
    price_currency = models.CharField(max_length=4 ,choices=currencies, default=currencies[0][0])
    price = models.PositiveIntegerField(blank=True, null=True)
    num_in_stock = models.PositiveIntegerField(blank=True, null=True)
    num_allocated = models.IntegerField(blank=True, null=True)
    low_stock_threshold = models.PositiveIntegerField(blank=True, null=True)
