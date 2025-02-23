from rest_framework import serializers
from ..models import Product
from typing import List, Dict


class ProductListCreateAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("title", "slug", "is_public", "updated_at")


class ProductDetailAdminSerializer(serializers.ModelSerializer):
    product_type = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "title", "slug", "is_public", "description", "meta_title", "meta_description", "created_at", "updated_at",
            "product_type", "categories"
        )

    def get_product_type(self, obj) -> Dict | None:
        if obj.product_type:
            return {"title": obj.product_type.title, "slug": obj.product_type.slug}
        return None

    def get_categories(self, obj) -> List:
        categories = list()
        for category in getattr(obj, "prefetched_categories", []):
            categories.append({"name": category.name, "slug": category.slug, "is_public": category.is_public})
        return categories
