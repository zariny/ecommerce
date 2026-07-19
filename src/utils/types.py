import strawberry
import strawberry_django
from . import models


@strawberry_django.interface(models.BaseSeoModel)
class BaseSeoModelType:
    meta_title: strawberry.auto
    meta_description: strawberry.auto


@strawberry_django.interface(models.ModelWithDescription)
class ModelWithDescriptionType:
    metadata: strawberry.auto
    description: strawberry.auto
