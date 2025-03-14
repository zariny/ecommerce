from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import generics
from django_filters import rest_framework as filters
from django.db.models import OuterRef, Subquery
from core.views import BaseAdminView, BaseAdminDetailView
from core.authenticate import JWTCookiesBaseAuthentication
from core.permissions import AdminSafeOrModelLvlPermission
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
    """
        View for listing and creating categories in a hierarchical structure.
        **HTTP Methods:**
        - GET: Retrieve a list of categories with nested children.
        - POST: Create a new category with specified position and optional relative_to.

        **Query Parameters (GET):**
        - is_public (bool): Filter by public visibility.
        - ancestors_are_public (bool): Filter by public ancestors.
        - is_root (bool): Filter root categories (depth=1).
        - child_of (int): Filter children of a specific category by ID.
        - search (str): Search by slug or name.
        - ordering (str): Order by 'path' or 'depth'.

        **Request Body (POST):**
        - name (str): Category name.
        - position (str): One of 'root', 'first_child_of', 'after', 'before'.
        - relative_to (int, optional): ID of the reference category (required unless position is 'root').
        - Other fields: slug, description, etc.

        **Response (GET):**
        - JSON list of categories with fields like pk, name, is_public, and children (nested).

        **Response (POST):**
        - JSON object of the created category.
    """
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategoryAdminSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("slug", "name")
    ordering_fields = ("path", "depth")
    filterset_class = CategoryFilterSet


class CategoryDetailAdminView(BaseAdminDetailView):
    """
        View for retrieving, updating, or deleting a single category.

        **HTTP Methods:**
        - GET: Retrieve details of a single category.
        - PUT/PATCH: Update category details, including repositioning.
        - DELETE: Remove the category.

        **URL Parameters:**
        - pk (int): The primary key of the category.

        **Request Body (PUT/PATCH):**
        - name (str, optional): Updated category name.
        - position (str, optional): One of 'root', 'first_child_of', 'after', 'before'.
        - relative_to (int, optional): ID of the reference category for repositioning.
        - Other fields: slug, description, etc.

        **Response (GET):**
        - JSON object with category details, including computed 'position' and 'relative_to'.

        **Response (PUT/PATCH):**
        - JSON object of the updated category.

        **Response (DELETE):**
        - 204 No Content on success.
    """
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategoryDeatilAdminSerializer


class CategoryNodeMovementView(generics.UpdateAPIView):
    """
        This specialized view is designed for reordering categories within the tree structure.
        It accepts a category ID and updates its position relative to another category,
        making it ideal for drag-and-drop interfaces in the frontend.

        **HTTP Methods:**
        - PUT/PATCH: Move the category to a new position.

        **URL Parameters:**
        - pk (int): The primary key of the category to move.

        **Request Body (PUT/PATCH):**
        - position (str): Required. One of 'root', 'first_child_of', 'after', 'before'.
        - relative_to (int, optional): ID of the reference category (required unless position is 'root').

        **Response:**
        - JSON object of the moved category with updated details.

        **Errors:**
        - 400 Bad Request: If position is invalid or relative_to is missing when required.

        **Frontend Note:**
        - Use this endpoint for drag-and-drop functionality. Refetch the category list after a successful move
          to reflect the updated hierarchy.
    """
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminSafeOrModelLvlPermission,)
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategoryNodeMovementAdminSerializer
