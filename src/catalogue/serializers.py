from rest_framework.serializers import ModelSerializer
from .models import Category


class CategoryListSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "slug", "background", "background_caption")


class CategoryDetailSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "pk", "name", "slug", "background", "background_caption", "meta_title", "meta_description", "description"
        )
