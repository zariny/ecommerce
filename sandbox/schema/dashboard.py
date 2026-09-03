import strawberry
from strawberry.schema.config import StrawberryConfig
from strawberry_django.optimizer import DjangoOptimizerExtension
from catalogue.dashboard import CatalogueQuery
from products.dashboard import ProductsQuery
from authentication import AuthenticateMutation


@strawberry.type
class Query(CatalogueQuery, ProductsQuery):
    node: strawberry.relay.Node = strawberry.relay.node()
    nodes: list[strawberry.relay.Node] = strawberry.relay.node()


@strawberry.type
class Mutation(AuthenticateMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    config=StrawberryConfig(relay_max_results=25),
    extensions=[DjangoOptimizerExtension],
)
