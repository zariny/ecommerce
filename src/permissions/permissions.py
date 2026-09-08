from .core import BasePermission, GrantPerm, ActionPerm


class DashboardPermission(BasePermission):
    DASHBOARD_ACCESS = GrantPerm(
        description="This permission grants access to the app dashboard.",
    )
    ACTIVE = ActionPerm(lambda user: user.is_active)
    ADMIN = ActionPerm(
        lambda user: user.is_staff and user.is_active,
        description="This permission is for accessing the internal admin panel.",
    )
    SUPERUSER = ActionPerm(lambda user: user.is_superuser and user.is_active)
