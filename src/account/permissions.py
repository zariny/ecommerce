from permissions.core import BasePermission, GrantPerm, ActionPerm


class AccountPermissions(BasePermission):
    USER_MANAGER = GrantPerm()
    GROUP_MANAGER = GrantPerm()
    VIEW_GROUP_SUBSCRIBERS = GrantPerm()
    VIEW_GROUP_PERMISSIONS = GrantPerm()
    VIEW_USER_PERMISSIONNS = GrantPerm()
    CHECK_SUPERUSER_STATUS = GrantPerm()
    CHECK_STAFF_STATUS = GrantPerm()

    CAN_DEL_SUPERUSERS = ActionPerm(
        lambda user, target: user.dated_joined > target.date_joined
    )
