from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import rest_framework as filters
from django.db.models import OuterRef, Subquery
from core.views import BaseAdminView, BaseAdminDetailView
from .. import models
from . import serializers


class CategoryFilterSet(filters.FilterSet):
    is_root = filters.BooleanFilter(method="root_filter", label="Is root category")
    child_of = filters.NumberFilter(method="children_filter", label="Child of")

    class Meta:
        model = models.Category
        fields = ("is_public", "ancestors_are_public")

    def root_filter(self, queryset, name, value):
        if value:
            return queryset.filter(depth=1)
        return queryset

    def children_filter(self, queryset, name, value):
        try:
            node = self.Meta.model.objects.get(pk=value)
            return node.get_children()
        except self.Meta.model.DoesNotExist:
            return queryset.none()


class CategoryAdminView(BaseAdminView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategoryAdminSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("slug", "name")
    ordering_fields = ("path", "depth")
    filterset_class = CategoryFilterSet


class CategoryDetailAdminView(BaseAdminDetailView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategoryDeatilAdminSerializer