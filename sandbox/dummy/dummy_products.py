from products.models import Product, ProductClass
from catalogue.models import Category, ProductCategory
from .abstraction import *


class DummyProductHandler(AbstractHandler):
    def __init__(self):
        self.faker = Faker()
        self.product_objects = list()
        self.product_category_objects = list()
        self.main_product_kls = ProductClass.objects.get_or_create(slug="main")

    def handle(self, flag, **kwargs):
        if flag:
            self.create_product()
            self.create_product_category()
            self.save()
            self.logger.info(
                f"Successfully created and saved {len(self.product_objects)} dummy product(s) to the database."
            )
        return super().handle(flag, **kwargs)

    def create_product(self):
        for _ in range(700):
            slug = self.faker.unique.word().capitalize()
            title = f"{self.faker.color_name()} {slug} of {self.faker.first_name()}"
            description = self.faker.text(max_nb_chars=300)
            self.product_objects.append(
                Product(
                    slug=slug,
                    title=title,
                    product_type=self.main_product_kls[0],
                    description=description
                )
            )

    def create_product_category(self):
        products_categories = set()
        categories = Category.objects.all()
        for _ in range(1000):
            product = random.choice(self.product_objects)
            category = random.choice(categories)

            key = (category.id, product.id)
            if key not in products_categories:
                products_categories.add(key)
                self.product_category_objects.append(
                    ProductCategory(
                        category=category,
                        product=product
                    )
                )

    def save(self):
        Product.objects.bulk_create(self.product_objects, batch_size=50)
        ProductCategory.objects.bulk_create(self.product_category_objects, batch_size=100)
