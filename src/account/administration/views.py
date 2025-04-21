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
