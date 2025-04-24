from faker import Faker
from django.contrib.auth import get_user_model
from order.models import Order
from .abstraction import AbstractHandler
from .utils import random_datetime
import random


class DummyOrderHandler(AbstractHandler):
    def __init__(self):
        self.orders = list()

    def handle(self, flag):
        self.create_orders()
        return super().handle(flag)

    def create_orders(self):
        User = get_user_model()
        users = User.objects.all()
        for _ in range(1000):
            self.orders.append(
                Order(
                    user=random.choice(users),
                    date_updated=random_datetime()
                )
            )
        self.save()

    def save(self):
        Order.objects.bulk_create(self.orders, batch_size=50)
