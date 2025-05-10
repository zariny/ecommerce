from django.db.models import Count, Q
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from core.views import BaseAdminView, BaseAdminDetailView
from core.authenticate import JWTCookiesBaseAuthentication
from core.permissions import AdminAndModelLevelPermission
from .. import models
from . import serializers


class ProductFilterByCategoryAdmin(filters.FilterSet):
    category = filters.CharFilter(method="filter_category")

    def filter_category(self, queryset, name, value):
        return queryset.filter(categories__slug__icontains=value).distinct()

    class Meta:
        model = models.Product
        fields = ("category",)


class ProductAdminView(BaseAdminView):
    """
    API view for listing and creating products in the dashboard panel.

    Provides authentication and permission controls for dashboard users.
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
    queryset = models.Product.objects.only("pk", "title", "slug", "is_public", "updated_at")
    serializer_class = serializers.ProductAdminSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilterByCategoryAdmin
    search_fields = ("title", "slug")


class ProductDetailAdminView(BaseAdminDetailView):
    """
    API view for retrieving and updating product details in the dashboard panel.
    Supports retrieving product details, including related product type and prefetching categories.

    note:
        authentication: The authentication mechanism used
        permission_classes: The permissions required (Admin user and other permissions).
        data: The base queryset with selected fields and prefetching.
        lookup_field: The field used for lookup (slug).
    """
    queryset = models.Product.objects.select_related(
        "product_type"
    ).only(
        "pk", "title", "slug", "is_public", "description", "meta_title", "meta_description", "created_at", "updated_at",
        "product_type__title"
    )
    serializer_class = serializers.ProductDetailAdminSerializer


class ProductAttributeAdminView(BaseAdminView):
    queryset = models.ProductAttribute.objects.only("pk", "name", "slug", "value_type")
    serializer_class = serializers.ProductAttributeAdminSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = ("require", "value_type")
    search_fields = ("slug", "name")


class ProductAttributeDetailAdminView(BaseAdminDetailView):
    queryset = models.ProductAttribute.objects.all()
    serializer_class = serializers.ProductAttributeDetailAdminSerializer


class ProductClassAdminView(BaseAdminView):
    queryset = models.ProductClass.objects.all()
    serializer_class = serializers.ProductClassAdminSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = ("require_shipping", "track_stock", "abstract")
    search_fields = ("slug", "title")


class ProductClassDetailAdminView(BaseAdminDetailView):
    queryset = models.ProductClass.objects.all()
    serializer_class = serializers.ProductClassDetailAdminSerializer


class ProductCountView(generics.GenericAPIView):
    """
    API view that returns the total count of public products and the count of products that are in stock.
    - The response is cached for 2 hours
    Returns:
        JSON object with:
            - total: Total number of public products.
            - instock: Number of public products with stockrecords indicating more than 1 item in stock.
    """
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminAndModelLevelPermission,)
    queryset = models.Product.objects.filter(is_public=True)

    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = queryset.aggregate(
            total=Count("pk"),
            instock=Count(expression="pk", filter=Q(stockrecords__num_in_stock__gt=1))
        )
        return Response(queryset)
