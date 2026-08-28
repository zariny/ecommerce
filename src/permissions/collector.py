import importlib
import inspect

from django.apps import apps

from .core import BasePermission
from .models import Permission


def collect_permission_classes():
    permissions = []

    for app_config in apps.get_app_configs():
        try:
            module = importlib.import_module(f"{app_config.name}.permissions")
        except ModuleNotFoundError as e:
            if e.name == f"{app_config.name}.permissions":
                continue
            raise

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(cls, BasePermission)
                and cls is not BasePermission
                and cls.__module__ == module.__name__
            ):
                permissions.append(cls)

    return permissions


def collect_grant_permissions():
    collected = set()
    for cls in collect_permission_classes():
        for perm in cls:
            if perm.db_value in collected:
                raise ValueError(f"Duplicated permission name: {perm}")
            if perm.is_grant:
                collected.add(perm)
    return collected


def sync_enum_permissions():
    content_type = Permission.objects.enum_permission
    current_codenames = set()

    for permission in collect_grant_permissions():
        codename = permission.db_value

        if codename in current_codenames:
            raise ValueError(f"Duplicate permission codename found: {codename!r}")

        Permission.objects.update_or_create(
            content_type=content_type,
            codename=codename,
            defaults={"name": permission.name},
        )

        current_codenames.add(codename)

    Permission.objects.filter(
        content_type=content_type,
    ).exclude(
        codename__in=current_codenames,
    ).delete()
