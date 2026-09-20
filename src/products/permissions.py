from permissions.core import BasePermission, GrantPerm


class ProductPermission(BasePermission):
    PRODUCT_MANAGER = GrantPerm()
