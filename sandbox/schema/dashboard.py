import strawberry
from catalogue.dashboard import CatalogueQuery, CatalogueMutation


@strawberry.type
class Query(CatalogueQuery):
    test: str = strawberry.field(lambda: "Hello world")


schema = strawberry.Schema(query=Query)
