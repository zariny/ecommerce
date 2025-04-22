from django.db import models
from core.models import DatedModel


class Order(DatedModel):  # TODO need status pipeline
    basket = models.ForeignKey("basket.Basket", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True, blank=True)
    shipping_code = models.CharField(max_length=128, default="", blank=True)
