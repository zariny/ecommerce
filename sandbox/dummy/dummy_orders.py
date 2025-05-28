import random

from django.contrib.auth import get_user_model
from order.models import Order, OrderLine
from products.models import Product
from inventory.models import StockRecord
from .abstraction import *
from .utils import random_datetime


class DummyOrderHandler(AbstractHandler):
    def __init__(self):
        self.orders = list()
        self.order_lines = list()
        self.products = Product.objects.all()

    def handle(self, flag, **kwargs):
        if flag:
            self.create_orders()
            self.create_order_lines()
            self.save()
            self.logger.info(f"Successfully created and saved {len(self.orders)} dummy order(s) to the database.")
        return super().handle(flag, **kwargs)

    def create_orders(self):
        User = get_user_model()
        users = User.objects.all()
        for _ in range(1000):
            price = random.uniform(1.1, 150.9)
            price = int(price*100) / 100
            self.orders.append(
                Order(
                    user=random.choice(users),
                    date_updated=random_datetime(),
                    date_created=random_datetime(),
                    status="complete",
                    total_excl_tax=price,
                    total_incl_tax=price + 2.1,
                    date_placed=random_datetime()
                )
            )

    def create_order_lines(self):
        default_stockrecord = StockRecord.objects.get_or_create(product=Product.objects.first())[0]
        for _ in range(931):
            price = random.uniform(1.1, 150.9)
            price = int(price*100) / 100
            self.order_lines.append(
                OrderLine(
                    order=random.choice(self.orders),
                    product=random.choice(self.products),
                    stockrecord=default_stockrecord,
                    quantity=random.randrange(20, 35),
                    line_price_incl_tax=price,
                    line_price_excl_tax=price,
                    line_price_before_discounts_incl_tax=price,
                    unit_price_incl_tax=price,
                    line_price_before_discounts_excl_tax=price
                )
            )

    def save(self):
        Order.objects.bulk_create(self.orders, batch_size=50)
        OrderLine.objects.bulk_create(self.order_lines, batch_size=100)
