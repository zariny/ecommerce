from rest_framework import serializers
from .models import Product


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("title", "slug")


class ProductDetailSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("title", "slug", "categories", "description", "meta_title", "meta_description")

    def get_categories(self, obj):
        # Use the prefetched data instead of making a new DB query
        return [{"name": cat.name, "slug": cat.slug} for cat in getattr(obj, "prefetched_categories", [])]
