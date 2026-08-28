from typing import Self
from asgiref.sync import sync_to_async
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import (
    Permission as AuthPermission,
    PermissionManager as AuthPermissionManager,
)
from account.models import User


class EnumPermission(models.Model):
    class Meta:
        managed = False


class PermissionManager(AuthPermissionManager):
    _enum_permission = None  # EnumPermission content type

    def get_queryset(self):
        return super().get_queryset().filter(content_type=self.enum_permission)

    @property
    def enum_permission(self) -> ContentType[EnumPermission]:
        if self._enum_permission is None:
            self._enum_permission = ContentType.objects.get_for_model(EnumPermission)
        return self._enum_permission


class Permission(AuthPermission):
    objects = PermissionManager()

    class Meta:
        proxy = True

    @classmethod
    def user_permissions(cls, user: User) -> models.QuerySet[Self]:
        return cls._default_manager.filter(
            models.Q(user=user) | models.Q(group__user=user)
        ).distinct()

    @classmethod
    async def auser_permissions(cls, user: User) -> list[Self]:
        qs = await sync_to_async(cls.user_permissions)(user)
        return [perm async for perm in qs]
