from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth import get_user_model
from rest_framework import generics
from core.permissions import AdminSafeOrModelLvlPermission
from core.authenticate import JWTCookiesBaseAuthentication
from core.views import ListLimitOffsetPagination
from . import serializers


User = get_user_model()

class UserListAdminView(generics.ListAPIView):
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminSafeOrModelLvlPermission,)
    queryset = User.objects.only("email", "is_staff", "is_active", "last_login")
    serializer_class = serializers.UserListAdminSerializer
    pagination_class = ListLimitOffsetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_fields = ("is_staff", "is_active")
    search_fields = ("email",)
    ordering_fields = ("email", "last_login")


class UserDetailAdminView(generics.RetrieveAPIView):
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminSafeOrModelLvlPermission,)
    queryset = User.objects.all()
    serializer_class = serializers.UserDetailAdminSerializer
