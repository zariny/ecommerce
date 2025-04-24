from .dummy_users import DummyUsersHandler
from .dummy_categories import DummyCategoryHandler
from .dummy_orders import DummyOrderHandler
from .dummy_products import DummyProductHandler


def run(flag): 	# Chain of Responsibility
    if flag:
        users = DummyUsersHandler()
        products = DummyProductHandler()
        products.set_next(DummyOrderHandler())
        categories = DummyCategoryHandler()
        categories.set_next(products)
        users.set_next(categories)

        flag = users.handle(flag)

    return flag
