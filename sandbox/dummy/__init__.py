from django.contrib.auth import get_user_model
from .dummy_users import DummyUsersHandler
from .dummy_categories import DummyCategoryHandler
from .dummy_orders import DummyOrderHandler
from .dummy_products import DummyProductHandler


User = get_user_model()


def run(flag): 	# Chain of Responsibility
    if flag and not User.objects.exists():
        users = DummyUsersHandler()
        products = DummyProductHandler()
        products.set_next(DummyOrderHandler())
        categories = DummyCategoryHandler()
        categories.set_next(products)
        users.set_next(categories)

        flag = users.handle(flag)

    return flag
