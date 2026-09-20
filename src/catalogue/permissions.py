from permissions.core import BasePermission, GrantPerm


class CataloguePermission(BasePermission):
    CATALOGUE_MANAGER = GrantPerm()
