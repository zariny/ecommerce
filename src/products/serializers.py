from rest_framework import serializers
from . import models
from typing import List


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ("title", "slug")


class ProductDetailSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = ("title", "slug", "categories", "description", "meta_title", "meta_description")

    def get_categories(self, obj) -> List:
        # Use the prefetched data instead of making a new DB query
        return [{"name": cat.name, "slug": cat.slug} for cat in getattr(obj, "prefetched_categories", [])]
