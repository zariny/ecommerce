import random
from faker import Faker
from django.contrib.auth import get_user_model
from sandbox.settings import CORE_LANGUAGES
from .utils import random_datetime
from .abstraction import AbstractHandler


class DummyUsersHandler(AbstractHandler):
    def __init__(self):
        self.faker = Faker()
        self.model = get_user_model()
        self.users = list()

    def handle(self, flag):
        if flag:
            self.create_users()
            return super().handle(flag)

    def create_users(self):
        for _ in range(500):
            email = self.faker.unique.email()
            name = self.faker.unique.name().split(" ")
            last_name = name[-1]
            first_name = " ".join(name[:-1])
            is_confirmed = random.choice([True, False])
            is_staff = random.choices([True, False], weights=[10, 90], k=1)[0]
            is_active = random.choices([True, False], weights=[95, 5], k=1)[0]
            language_code = random.choice(CORE_LANGUAGES)[0]
            last_login = random_datetime()
            self.users.append(
                self.model(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    is_confirmed=is_confirmed,
                    is_staff=is_staff,
                    is_active=is_active,
                    language_code=language_code,
                    last_login=last_login
                )
            )

        self.save()

    def save(self):
        self.model._default_manager.bulk_create(self.users, batch_size=50)
