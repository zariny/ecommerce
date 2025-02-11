from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import generics
from django_filters import rest_framework as filters
from .models import Category
from .serializers import CategoryListSerializer, CategoryDetailSerializer


class CategoryPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 30


class CategoryRootFilter(filters.FilterSet):
    root = filters.BooleanFilter(method="root_filter")

    class Meta:
        model = Category
        fields = ("depth",)

    def root_filter(self, queryset, name, value):
        if value:
            return queryset.filter(depth=1)
        return queryset


class CategoryList(generics.ListAPIView):
    """
    API view for listing categories.
    - Supports filtering, searching, and ordering on (name & slug) fields.
    - Paginates results with defauly=10, max_limit=30.
    """
    queryset = Category.objects.browsable().only(
        "pk", "name", "slug", "background", "background_caption"
    ).order_by("path")
    serializer_class = CategoryListSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = CategoryRootFilter
    pagination_class = CategoryPagination
    search_fields = ("name", "slug")
    ordering_fields = ("path", "depth")


class CategoryDetail(generics.RetrieveAPIView):
    """
    API view for retrieving category details.
    - Returns category details along with its direct children.
    """
    queryset = Category.objects.browsable().filter().only(
        "pk", "name", "slug", "background", "background_caption", "meta_title", "meta_description", "description"
    )
    serializer_class = CategoryDetailSerializer
    lookup_field = "slug"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serdata = self.get_serializer(instance).data
        children = instance.get_children().browsable().only("pk", "name", "slug", "background", "background_caption")
        serdata["children"] = CategoryListSerializer(children, many=True).data
        return Response(serdata)
