import strawberry
from strawberry.schema.config import StrawberryConfig
from strawberry_django.optimizer import DjangoOptimizerExtension
from catalogue.dashboard import CatalogueQuery
from products.dashboard import ProductsQuery
from authentication import AuthenticateMutation

from permissions.integrations import with_permission
from permissions.permissions import DashboardPermission as P


@with_permission(P.DASHBOARD_ACCESS)
@strawberry.type
class Query(CatalogueQuery, ProductsQuery):
    node: strawberry.relay.Node = (
        strawberry.relay.node()
    )  # NOTE These nodes are not protected by any permissions!
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
