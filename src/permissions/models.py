from typing import Self
from asgiref.sync import sync_to_async
from django.db import models
from django.contrib.auth.models import (
    Permission as AuthPermission,
    PermissionManager as AuthPermissionManager,
)
from account.models import User
from itertools import groupby
from dataclasses import dataclass


@dataclass
class PermissionCluster:
    name: str
    branches: list["Permission"]


class EnumPermission(models.Model):
    class Meta:
        managed = False


class PermissionManager(AuthPermissionManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                content_type__app_label=EnumPermission._meta.app_label,
                content_type__model=EnumPermission._meta.model_name,
            )
        )

    def clusters(self):
        perms = self.get_queryset().order_by("codename")
        return [
            PermissionCluster(name=cluster_name, branches=list(group))
            for cluster_name, group in groupby(
                perms, key=lambda p: p.codename.partition(".")[0]
            )
        ]


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
