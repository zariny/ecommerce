from strawberry.extensions import FieldExtension
from strawberry import Info
from permissions.core import BasePermission, check_grant_permissions
from strawberry_django.permissions import DjangoNoPermission
from collections.abc import Iterable


# NOTE Only define resolve_async here (not resolve).
# graphql-core picks sync vs async per-field based on whether resolve_async
# exists. Having both can make it choose the sync `resolve` path even
# under ASGI, causing Django's ORM/session access to run inside the
# event loop thread -> SynchronousOnlyOperation.
class Permission(FieldExtension):
    def __init__(self, permissions: Iterable[BaseException] | BasePermission):
        self.permissions = permissions  # NOTE only GrantPerm is allow

    async def resolve_async(self, next_, source, info: Info, **kwargs):
        user = await info.context.request.auser()
        if not user.is_authenticated or not user.is_active:
            raise DjangoNoPermission("Your user does not have access.")

        denied = await check_grant_permissions(user, self.permissions)

        if not denied:
            return await next_(source, info, **kwargs)
        raise DjangoNoPermission(
            f"You don't have these permissions for this action: {', '.join(perm.name for perm in denied)}"
        )


def with_permission(permissions):
    def wrapper(cls):
        for field in cls.__strawberry_definition__.fields:
            field.extensions = [*(field.extensions or []), Permission(permissions)]
        return cls

    return wrapper
