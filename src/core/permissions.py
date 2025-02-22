from rest_framework.permissions import IsAdminUser, DjangoModelPermissions


class AdminSafeOrModelLvlPermission(IsAdminUser, DjangoModelPermissions):
    pass
