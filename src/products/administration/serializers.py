from rest_framework import serializers
from catalogue.models import Category
from .. import models
from typing import Dict


class ProductAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ("pk", "title", "slug", "is_public", "updated_at")


class ProductDetailAdminSerializer(serializers.ModelSerializer):
    product_type = serializers.SerializerMethodField()
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = models.Product
        fields = (
            "title", "slug", "is_public", "description", "meta_title", "meta_description", "created_at", "updated_at",
            "product_type", "categories"
        )

    def get_product_type(self, obj) -> Dict | None:
        if obj.product_type:
            return {"title": obj.product_type.title, "slug": obj.product_type.slug}
        return None

    def to_representation(self, instance):
        representation =  super().to_representation(instance)

        categories = list()
        for category in instance.categories.all().only("pk", "name", "is_public"):
            categories.append({"pk": category.pk, "name": category.name, "is_public": category.is_public})
        representation["categories"] = categories
        return representation


class ProductAttributeAdminSerializer(serializers.ModelSerializer):
    product_class = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductClass.objects.all(), many=True, required=False, write_only=True,
    )

    class Meta:
        model = models.ProductAttribute
        fields = "__all__"
        extra_kwargs ={
            "require": {"write_only": True},
            "slug": {"write_only": True},
        }


class ProductAttributeDetailAdminSerializer(serializers.ModelSerializer):
    product_class = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductClass.objects.all(), write_only=True, many=True, required=False
    )

    class Meta:
        model = models.ProductAttribute
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        product_classes = []
        for product_class in instance.product_class.only("pk", "title"):
            product_classes.append({"pk": product_class.pk, "title": product_class.title})
        representation["product_class"] = product_classes
        return representation
