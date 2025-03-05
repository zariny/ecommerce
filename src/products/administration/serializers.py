from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework import serializers
from catalogue.models import Category
from .. import models
from typing import Dict


class ProductAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ("pk", "title", "slug", "is_public", "updated_at")


class ProductDetailAdminSerializer(serializers.ModelSerializer):
    class ProductAttributeValueSerializer(serializers.ModelSerializer):
        class Meta:
            model = models.ProductAttributeValue
            fields  = ("attribute", "value")

        def validate(self, attrs):
            value = attrs.pop("value")
            field = models.ProductAttributeValue._meta.get_field("value")
            try:
                value = field.clean(value=value, datatype=attrs.get("attribute").value_type, model_instance=None)
            except DjangoValidationError as e:
                message = {"attribute": attrs["attribute"].pk, "value": str(e)}
                raise RestValidationError(message)
            attrs["value"] = value
            return super().validate(attrs)


    product_type = serializers.SerializerMethodField()
    attribute_values = ProductAttributeValueSerializer(many=True, required=False, write_only=True)
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
            "product_type", "categories", "attribute_values"
        )

    def get_product_type(self, obj) -> Dict | None:
        if obj.product_type:
            return {"title": obj.product_type.title, "slug": obj.product_type.slug}
        return None

    def to_representation(self, instance):
        representation =  super().to_representation(instance)

        categories = list()
        for i in instance.categories.all().only("name", "is_public"):
            categories.append({"name": i.name, "is_public": i.is_public})
        representation["categories"] = categories

        attribute_values = list()
        for attr_val in instance.attr.all():
            attribute_values.append(
                {
                    "attribute": attr_val.attribute.pk,
                    "name": attr_val.attribute.name,
                    "value": attr_val.value,
                    "value_type": attr_val.value_type
                }
            )

        representation["attribute_values"] = attribute_values
        return representation

    def update(self, instance, validated_data):
        attribute_values = validated_data.pop("attribute_values", [])
        instance = super().update(instance, validated_data)
        if attribute_values:
            ...
        return instance


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
