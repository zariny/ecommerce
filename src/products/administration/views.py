from rest_framework import generics
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from core.authenticate import JWTCookiesBaseAuthentication
from core.permissions import AdminSafeOrModelLvlPermission
from core.views import ListLimitOffsetPagination
from .. import models
from . import serializers


class ProductFilterByCategoryAdmin(filters.FilterSet):
    category = filters.CharFilter(method="filter_category")

    def filter_category(self, queryset, name, value):
        return queryset.filter(categories__slug__icontains=value).distinct()

    class Meta:
        model = models.Product
        fields = ("category",)


class ProductListCreateAdmin(generics.ListCreateAPIView):
    """
    API view for listing and creating products in the administration panel.

    Provides authentication and permission controls for administration users.
    Supports filtering, searching, and pagination.

    note:
        authentication: The authentication mechanism used
        permission_classes: The permissions required (Admin user and other permissions).
        The base queryset selecting specific fields of Product: "pk", "title", "slug", "is_public", "updated_at"
        filter_backends: The backend filters (SearchFilter).
        FilterSet: The filter class for category-based filtering.
        Pagination: The pagination class used for listing.
        search_fields: Fields that support search (title, slug).
    """
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminSafeOrModelLvlPermission,)
    queryset = models.Product.objects.only("pk", "title", "slug", "is_public", "updated_at")
    serializer_class = serializers.ProductAdminSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilterByCategoryAdmin
    pagination_class = ListLimitOffsetPagination
    search_fields = ("title", "slug")


class ProductRetrieveUpdateAdmin(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating product details in the administration panel.
    Supports retrieving product details, including related product type and prefetching categories.

    note:
        authentication: The authentication mechanism used
        permission_classes: The permissions required (Admin user and other permissions).
        data: The base queryset with selected fields and prefetching.
        lookup_field: The field used for lookup (slug).
    """
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminSafeOrModelLvlPermission,)
    queryset = models.Product.objects.select_related(
        "product_type"
    ).only(
        "pk", "title", "slug", "is_public", "description", "meta_title", "meta_description", "created_at", "updated_at",
        "product_type__title"
    )
    serializer_class = serializers.ProductDetailAdminSerializer


class ProductAttributeListCreateAdmin(generics.ListCreateAPIView):
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminSafeOrModelLvlPermission,)
    queryset = models.ProductAttribute.objects.only("pk", "name", "slug", "value_type")
    serializer_class = serializers.ProductAttributeAdminSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    pagination_class = ListLimitOffsetPagination
    filterset_fields = ("require", "value_type")
    search_fields = ("slug", "name")


class ProductAttributeDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminSafeOrModelLvlPermission,)
    queryset = models.ProductAttribute.objects.all()
    serializer_class = serializers.ProductAttributeDetailAdminSerializer


class ProductClassListCreateAdmin(generics.ListCreateAPIView):
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminSafeOrModelLvlPermission,)
    queryset = models.ProductClass.objects.all()
    serializer_class = serializers.ProductClassAdminSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    pagination_class = ListLimitOffsetPagination
    filterset_fields = ("require_shipping", "track_stock", "abstract")
    search_fields = ("slug", "title")


class ProductClassDetailAdmin(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminSafeOrModelLvlPermission,)
    queryset = models.ProductClass.objects.all()
    serializer_class = serializers.ProductClassDetailAdminSerializer
