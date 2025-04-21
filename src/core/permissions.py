from rest_framework.permissions import BasePermission, IsAdminUser, DjangoModelPermissions


class StrictDjangoModelPermissions(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class AdminAndModelLevelPermission(BasePermission):
    def has_permission(self, request, view):
        return (
                IsAdminUser().has_permission(request, view)
                and
                StrictDjangoModelPermissions().has_permission(request, view)
        )

    def has_object_permission(self, request, view, obj):
        return StrictDjangoModelPermissions().has_object_permission(request, view, obj)
