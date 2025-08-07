from django.contrib.auth import get_user_model
from django.db.models.functions import TruncDay, TruncMonth
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from utils.permissions import AdminAndModelLevelPermission
from utils.authenticate import JWTCookiesBaseAuthentication
from utils.views import ListLimitOffsetPagination
from utils.filters import DateRangeFilterSet
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


class AdminUserRoleView(generics.GenericAPIView): # TODO need develop
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
        such as PUT, PATCH, DELETE, or POST. However, the user MAY ONLY HAVE PERMISSION TO SOME of these methods.

    - SUPERUSER:
        Has full unrestricted access across all apps and endpoints.

    This view returns the current authenticated admin user's roles and permissions.
    It's used by the frontend dashboard to determine which parts of the UI should be accessible.
    """
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (IsAdminUser,)
    serializer_class = serializers.UserRoleSerializer

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

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class UserDateRangeFilter(DateRangeFilterSet):
    class Meta:
        field_name = "date_joined"


class UserGrowthChartView(generics.ListAPIView):
    """
    API endpoint to retrieve user registration growth over time.

    This endpoint returns the number of new registered users grouped by day or month,
    depending on the selected date range. If no query parameters are provided,
    the default range is the past 30 days (grouped daily). If the date range exceeds
    40 days, results will be grouped monthly.
    """
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminAndModelLevelPermission,)
    queryset = User.objects.all()
    serializer_class = serializers.UserGrowthChartSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserDateRangeFilter

    def get(self, request, *args, **kwargs):
        filterset = self.filterset_class(data=request.GET, queryset=self.get_queryset(), request=request)

        if not filterset.is_valid():
            return Response(filterset.errors, status=400)

        proper_trunk = TruncDay if filterset.delta <= 30 else TruncMonth
        queryset = filterset.qs.annotate(date=proper_trunk("date_joined")).values("date").annotate(count=Count("pk"))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserCountView(APIView):
    """
    API endpoint to retrieve user statistics for use in visualizations such as a radial chart.
    Response Format:
    {
        total: int,
        confirmed_users: int
    }
    """
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminAndModelLevelPermission,)
    queryset = User.objects.all()

    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, *args, **kwargs):
        data = self.queryset.aggregate(
            total=Count("pk"),
            confirmed_users=Count("pk", filter=Q(is_confirmed=True))
        )
        return Response(data)
