from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Prefetch
from django_filters import rest_framework as filters
from catalogue.models import Category
from .serializers import ProductListSerializer, ProductDetailSerializer
from . import models


class ProductFilterByCategory(filters.FilterSet):
    category = filters.CharFilter(method="filter_public_category")

    def filter_public_category(self, queryset, name, value):
        return queryset.filter(
            categories__slug__icontains=value, categories__is_public=True, categories__ancestors_are_public=True
        ).distinct()

    class Meta:
        model = models.Product
        fields = ("category",)


class ProductPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 30


class ProductList(generics.ListAPIView):
    """
    API endpoint for retrieving a paginated list of public products.

    - Supports filtering by category slug.
    - Uses limit-offset pagination with a default limit of 10.

    **Query Parameters:**
    - `limit`: Number of products per page (default: 10, max: 30)
    - `offset`: Number of items to skip (for pagination)
    - `category`: Filter by category slug (case-insensitive, partial matching)
    """
    queryset = models.Product.objects.filter(is_public=True).only("pk", "title", "slug")
    serializer_class = ProductListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilterByCategory
    pagination_class = ProductPagination


class ProductDetail(generics.RetrieveAPIView):
    """
       API endpoint for retrieving the details of a single public product by its slug.

       **URL Parameter:**
       - `slug` (str): The unique slug identifier for the product.

       **Response Data:**
       - `title` (str): The product's title.
       - `slug` (str): The unique slug identifier.
       - `description` (str): A brief description of the product.
       - `meta_title` (str): SEO meta title for the product.
       - `meta_description` (str): SEO meta description for the product.
       - `categories` (list): A list of related categories, each containing:
         - `name` (str): The category name.
         - `slug` (str): The category slug.

       **Example Request:**
           GET /api/products/example1/

       **Example Response:**
       ```json
       {
           "title": "example 1",
           "slug": "example1",
           "description": "...",
           "meta_title": "...",
           "meta_description": "...",
           "categories": [
               {"name": "...", "slug": "..."},
               {"name": "...", "slug": "..."},
           ]
       }
       ```
    """
    queryset = models.Product.objects.filter(is_public=True).only(
        "pk", "title", "slug", "description", "meta_title", "meta_description"
    ).prefetch_related(
        Prefetch(
            "categories",
            queryset=Category.objects.only("id", "name", "slug").browsable(),
            to_attr="prefetched_categories",
        )
    )
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
