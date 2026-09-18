import strawberry
import strawberry_django
from ..models import Permission
from asgiref.sync import sync_to_async


@strawberry_django.type(Permission)
class PermissionType(strawberry.relay.Node):
    name: strawberry.auto
    codename: strawberry.auto


@strawberry.type
class PermissionClusterType:
    name: str
    permissions: list[PermissionType]


@strawberry.type
class PermissionQuery:
    @strawberry_django.field
    async def clusters(self) -> list[PermissionClusterType]:
        perm_clusters = await sync_to_async(Permission.objects.clusters)()
        return [
            PermissionClusterType(name=c.name, permissions=c.branches)
            for c in perm_clusters
        ]
