from django.db.transaction import rollback
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from core.permissions import AdminAndModelLevelPermission
from core.authenticate import JWTCookiesBaseAuthentication
from core.views import ListLimitOffsetPagination
from . import serializers


User = get_user_model()

class UserListAdminView(generics.ListAPIView):
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminAndModelLevelPermission,)
    queryset = User.objects.only("email", "is_staff", "is_active", "last_login")
    serializer_class = serializers.UserListAdminSerializer
    pagination_class = ListLimitOffsetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_fields = ("is_staff", "is_active")
    search_fields = ("email",)
    ordering_fields = ("email", "last_login")


class UserDetailAdminView(generics.RetrieveAPIView):
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminAndModelLevelPermission,)
    queryset = User.objects.all()
    serializer_class = serializers.UserDetailAdminSerializer


class AdminUserRoleView(APIView): # TODO need develop
    """
        Permission Levels:

    \n
    ┌────────────────────────────┐
    │         SUPERUSER          │
    ├────────────────────────────┤
    │          MANAGER           │
    ├────────────────────────────┤
    │           VIEWER           │
    ├────────────────────────────┤
    │           ADMIN            │
    └────────────────────────────┘
    \n.

    ------------------
    - ADMIN:
        Default fallback role for authenticated admin users without explicit group assignment.

    - VIEWER:
        Has permission to perform (safe HTTP methods) (GET, HEAD, OPTIONS)
        on endpoints of the app they have access to.

    - MANAGER:
        Has permission to perform (safe methods), also (modification methods)
        such as PUT, PATCH, DELETE, or POST. However, the user MAY ONLY HAVE PERMISSION to some these methods.

    - SUPERUSER:
        Has full unrestricted access across all apps and endpoints.

    This view returns the current authenticated admin user's roles and permissions.
    It's used by the frontend dashboard to determine which parts of the UI should be accessible.
    """
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (IsAdminUser,)

    def get(self, request):
        roles = list()
        if request.user.is_superuser:
            roles.append("superuser")
        else:
            roles += list(request.user.groups.values_list("name", flat=True))

        if not roles:
            roles.append("admin")

        data = {
            "roles": roles
        }
        return Response(data, status=status.HTTP_200_OK)
