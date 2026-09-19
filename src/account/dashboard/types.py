from django.db.models import Prefetch
import strawberry_django
from strawberry import auto
from strawberry.relay import Node
from permissions.models import Permission
from permissions.dashboard.query import PermissionType
from permissions.integrations import with_permission, Permission as Perm
from utils.relay import CursorConnection
from utils.types import ModelWithDescriptionType
from .. import models
from ..permissions import AccountPermissions as P


@strawberry_django.filter_type(models.User, lookups=True)
class UserFilterType:
    id: auto
    is_active: auto
    is_confirmed: auto
    is_superuser: auto
    is_staff: auto


@strawberry_django.order_type(models.User)
class UserOrderType:
    id: auto
    last_login: auto
    updated_at: auto
    email: auto


@with_permission(P.USER_MANAGER)
@strawberry_django.type(models.User, filters=UserFilterType, ordering=UserOrderType)
class UserType(Node, ModelWithDescriptionType):
    email: auto
    first_name: auto
    last_name: auto
    is_staff: auto = strawberry_django.field(extensions=[Perm(P.CHECK_STAFF_STATUS)])
    is_active: auto
    is_confirmed: auto
    is_superuser: auto = strawberry_django.field(
        extensions=[Perm(P.CHECK_SUPERUSER_STATUS)]
    )
    date_joined: auto
    updated_at: auto
    last_login: auto
    avatar: auto
    language_code: auto
    groups: list["GroupType"] = strawberry_django.field(
        extensions=[Perm(P.VIEW_GROUP_SUBSCRIBERS)]
    )

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.prefetch_related(
            Prefetch(
                "user_permissions",
                queryset=Permission.objects.all(),
                to_attr="_direct_permissions",
            ),
            Prefetch(
                "groups",
                queryset=models.Group.objects.prefetch_related(
                    Prefetch(
                        "permissions",
                        queryset=Permission.objects.all(),
                        to_attr="_permissions",
                    )
                ),
            ),
        )

    @strawberry_django.field(extensions=[Perm(P.VIEW_USER_PERMISSIONNS)])
    def permissions(self) -> list[PermissionType]:
        permissions = {}

        for p in getattr(self, "_direct_permissions", []):
            permissions[p.pk] = p

        return [
            PermissionType(
                codename=p.codename,
                name=p.name,
            )
            for p in permissions.values()
        ]

    @strawberry_django.field(extensions=[Perm(P.VIEW_GROUP_PERMISSIONS)])
    def group_permissions(self) -> list[PermissionType]:
        permissions = {}

        for group in self.groups.all():
            for p in getattr(group, "_permissions", []):
                permissions[p.pk] = p

        return [
            PermissionType(codename=p.codename, name=p.name)
            for p in permissions.values()
        ]


@with_permission(P.GROUP_MANAGER)
@strawberry_django.type(models.Group)
class GroupType(Node):
    name: auto
    permissions: list[PermissionType]
    user_set: CursorConnection[UserType] = strawberry_django.connection(
        name="users",
        extensions=[Perm(P.VIEW_GROUP_SUBSCRIBERS)],
        filters=UserFilterType,
        ordering=UserOrderType,
    )
