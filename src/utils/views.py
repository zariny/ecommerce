from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from . import permissions, authenticate


class ListLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 30


class BaseAdminView(generics.ListCreateAPIView):
    authentication_classes = (authenticate.JWTCookiesBaseAuthentication,)
    permission_classes = (permissions.AdminAndModelLevelPermission,)
    pagination_class = ListLimitOffsetPagination


class BaseAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (authenticate.JWTCookiesBaseAuthentication,)
    permission_classes = (permissions.AdminAndModelLevelPermission,)
