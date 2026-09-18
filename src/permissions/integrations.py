from collections.abc import Iterable
import strawberry
from strawberry.extensions import FieldExtension
from strawberry.types.field import StrawberryField
from strawberry import Info
from permissions.core import BasePermission, check_grant_permissions
from strawberry_django.permissions import DjangoNoPermission
from strawberry.schema_directive import Location
from graphql import parse


@strawberry.schema_directive(locations=[Location.FIELD_DEFINITION])
class RequiresPermission:
    permissions: list[str]


# NOTE Only define resolve_async here (not resolve).
# graphql-core picks sync vs async per-field based on whether resolve_async
# exists. Having both can make it choose the sync `resolve` path even
# under ASGI, causing Django's ORM/session access to run inside the
# event loop thread -> SynchronousOnlyOperation.
class Permission(FieldExtension):
    def __init__(self, permissions: Iterable[BaseException] | BasePermission):
        self.permissions: set = (
            {permissions}
            if isinstance(permissions, BasePermission)
            else set(permissions)
        )

    def apply(self, field: StrawberryField) -> None:
        existing_directive = next(
            (d for d in field.directives if isinstance(d, RequiresPermission)),
            None,
        )
        if existing_directive is not None:
            existing_directive.permissions = sorted(
                set(existing_directive.permissions) | {p.name for p in self.permissions}
            )
        else:
            field.directives.append(
                RequiresPermission(permissions=sorted(p.name for p in self.permissions))
            )

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


def with_permission(permissions: Iterable[BasePermission] | BasePermission):
    def wrapper(cls):
        perms = (
            {permissions}
            if isinstance(permissions, BasePermission)
            else set(permissions)
        )

        for field in cls.__strawberry_definition__.fields:
            field.extensions = field.extensions or []

            for ext in field.extensions:
                if isinstance(ext, Permission):
                    ext.permissions |= perms
                    break
            else:
                field.extensions = [*field.extensions, Permission(perms)]

        return cls

    return wrapper


@strawberry.type
class PermissionMetadataType:
    type_name: str
    field_name: str
    permissions: list[str]


@strawberry.type
class __PermissionMetadata:
    @strawberry.field(
        name="_fieldPermissions",
        description="🔒 Internal: lists which fields require which permissions, extracted from schema directives.",
    )
    def field_permissions(
        self,
        info: strawberry.Info,
        type_name: str | None = None,
        field_name: str | None = None,
    ) -> list[PermissionMetadataType]:
        permissions = _extract_metadata_permissions(info.schema)

        if type_name:
            permissions = [
                p for p in permissions if p.type_name.lower() == type_name.lower()
            ]

        if field_name:
            permissions = [
                p for p in permissions if p.field_name.lower() == field_name.lower()
            ]

        return permissions


def _extract_metadata_permissions(schema):
    """
    NOTE HACK
    Extract @requiresPermission directives from the schema'
    GraphQL introspection has no standard `appliedDirectives` field (it was
    proposed but never merged into the spec), so directives on a field
    definition can't be read via a normal introspection query. We work
    around this by printing the schema to SDL and re-parsing it, then
    reading the directive nodes directly from the AST.
    """
    sdl = schema.as_str()
    document = parse(sdl)
    result: list[PermissionMetadataType] = []

    for definition in document.definitions:
        fields = getattr(definition, "fields", None)
        if not fields:
            continue

        type_name = definition.name.value

        for field in fields:
            if not field.directives:
                continue

            for directive in field.directives:
                if directive.name.value != "requiresPermission":
                    continue

                permissions = [
                    v.value
                    for arg in directive.arguments
                    if arg.name.value == "permissions"
                    for v in arg.value.values
                ]

                result.append(
                    PermissionMetadataType(
                        type_name=type_name,
                        field_name=field.name.value,
                        permissions=permissions,
                    )
                )

    return result
