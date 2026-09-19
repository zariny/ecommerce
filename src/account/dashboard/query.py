import strawberry_django
import strawberry
from utils.relay import CursorConnection
from . import types


@strawberry.type
class AccountQuery:
    users: CursorConnection[types.UserType] = strawberry_django.connection()
    user: types.UserType = strawberry_django.node()
    groups: CursorConnection[types.GroupType] = strawberry_django.connection()
    group: types.GroupType = strawberry_django.node()
