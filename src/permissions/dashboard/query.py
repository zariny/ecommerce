import strawberry
import strawberry_django
from ..models import Permission
from asgiref.sync import sync_to_async
from django.contrib.auth.models import Permission as AuthPermission
from permissions.integrations import with_permission
from ..permissions import PermissionManager as P


@strawberry_django.filter_type(AuthPermission, lookups=True)
class PermissionFilterType:
    name: strawberry.auto


@strawberry_django.type(AuthPermission, filters=PermissionFilterType)
class PermissionType(strawberry.relay.Node):
    name: strawberry.auto
    codename: strawberry.auto

    @classmethod
    def get_queryset(cls, queryset, info, **kwargs):
        return queryset.filter(content_type_id=Permission.objects.enum_permission.pk)


@strawberry.type
class PermissionClusterType:
    label: str
    permissions: list[PermissionType] = strawberry_django.field(
        filters=PermissionFilterType  # FIXME it's not work!
    )


@with_permission(P.PERMISSION_MANAGER)
@strawberry.type
class PermissionQuery:
    @strawberry_django.field
    async def permissions(self) -> list[PermissionClusterType]:
        perm_clusters = await sync_to_async(Permission.objects.clusters)()
        return [
            PermissionClusterType(label=c.name, permissions=c.branches)
            for c in perm_clusters
        ]
