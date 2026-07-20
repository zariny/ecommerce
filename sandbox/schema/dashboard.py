import strawberry
from strawberry.schema.config import StrawberryConfig
from catalogue.dashboard import CatalogueQuery
from strawberry_django.optimizer import DjangoOptimizerExtension


@strawberry.type
class Query(CatalogueQuery):
    node: strawberry.relay.Node = strawberry.relay.node()
    nodes: list[strawberry.relay.Node] = strawberry.relay.node()


schema = strawberry.Schema(
    query=Query,
    config=StrawberryConfig(relay_max_results=10),
    extensions=[DjangoOptimizerExtension],
)
