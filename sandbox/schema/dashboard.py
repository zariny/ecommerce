import strawberry
from strawberry.schema.config import StrawberryConfig
from strawberry_django.optimizer import DjangoOptimizerExtension
from catalogue.dashboard import CatalogueQuery
from products.dashboard import ProductsQuery
from authentication import AuthenticateMutation
from permissions.dashboard.query import PermissionQuery
from permissions.integrations import __PermissionMetadata, with_permission
from permissions.permissions import DashboardPermission as P
from account.dashboard.query import AccountQuery


@with_permission(P.DASHBOARD_ACCESS)
@strawberry.type
class Query(
    CatalogueQuery,
    ProductsQuery,
    PermissionQuery,
    AccountQuery,
    __PermissionMetadata,
):
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
