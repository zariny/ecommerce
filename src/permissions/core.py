import enum
from collections.abc import Callable

from collections.abc import Iterable

from .models import Permission
from account.models import User


class GrantPerm:
    __slots__ = ("denial_msg", "description")

    def __init__(self, description: str | None = None, denial_msg: str | None = None):
        self.description = description
        self.denial_msg = denial_msg

    def __repr__(self):
        return f"Declared(description={self.description!r})"


class ActionPerm:
    __slots__ = ("denial_msg", "description", "func")

    def __init__(
        self,
        func: Callable[..., bool],
        /,
        description: str | None = None,
        denial_msg: str | None = None,
    ):
        self.func = func
        self.description = description
        self.denial_msg = denial_msg

    def __repr__(self):
        return f"Action(func={self.func!r})"


class BasePermission(enum.Enum):
    def __new__(cls, marker: GrantPerm | ActionPerm):
        if not isinstance(marker, (GrantPerm, ActionPerm)):
            raise TypeError(
                f"{cls.__name__} members must be assigned a GrantPerm(...) or ActionPerm(...) instance, got {marker!r}"
            )
        obj = object.__new__(cls)
        obj._value_ = marker
        return obj

    def __and__(self, other):
        if isinstance(other, list):
            if self not in other:
                other.append(self)
            return other
        return [self, other]

    def __rand__(self, other):
        return self.__and__(other)

    @property
    def is_grant(self) -> bool:
        return isinstance(self.value, GrantPerm)

    @property
    def is_action(self) -> bool:
        return isinstance(self.value, ActionPerm)

    @property
    def description(self) -> str | None:
        return self.value.description

    @property
    def db_value(self) -> str:
        """What gets stored in the database - always enum name & the member name."""
        return f"{self.__class__.__name__}.{self.name}"

    @property
    def denial_message(self):
        return (
            self.value.denial_msg
            or f"You don't have {self.name} permission for this action"
        )


async def check_grant_permissions(
    user: User, permission: BasePermission | Iterable[BaseException]
) -> set[BasePermission]:
    denied = set()

    if user.is_superuser:
        return denied

    if isinstance(permission, BasePermission):
        permission = {permission}

    resolved = await Permission.auser_permissions(user)
    code_names = [i.codename for i in resolved]

    for perm in permission:
        if not perm.is_grant:
            raise TypeError(f"{perm} is not a GrantPerm")
        if perm.db_value not in code_names:
            denied.add(perm)

    return denied
