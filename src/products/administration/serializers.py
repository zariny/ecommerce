from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework import serializers
from catalogue.models import Category
from .. import models


class BaseProductAdminSerializer(serializers.ModelSerializer):
    class ProductAttributeValueSerializer(serializers.ModelSerializer):
        class Meta:
            model = models.ProductAttributeValue
            fields  = ("attribute", "value")

        def validate(self, attrs):
            value = attrs.pop("value")
            field = self.Meta.model._meta.get_field('value')
            try:
                value = field.clean(value=value, datatype=attrs.get("attribute").value_type, model_instance=None)
            except DjangoValidationError as e:
                message = {"attribute": attrs["attribute"].pk, "value": str(e)}
                raise RestValidationError(message)
            attrs["value"] = value
            return super().validate(attrs)


    attributes = ProductAttributeValueSerializer(many=True, required=False, write_only=True)
    product_type = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductClass.objects.all(),
        many=False,
        write_only=True,
        required=True
    )
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        write_only=True,
        required=False
    )


class ProductAdminSerializer(BaseProductAdminSerializer):
    class Meta:
        model = models.Product
        exclude = ("attributes", "created_at")
        extra_kwargs = {
            "meta_title": {"write_only": True},
            "meta_description": {"write_only": True},
            "description": {"write_only": True}
        }


class ProductDetailAdminSerializer(BaseProductAdminSerializer):
    class Meta:
        model = models.Product
        fields = "__all__"

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation["product_type"] = {"pk": instance.product_type.pk, "title": instance.product_type.title}
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
            instance.attr._dirty = attribute_values
            instance.attr.save()
        return instance


class BaseProductAttributeAdminSerializer(serializers.ModelSerializer):
    product_class = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductClass.objects.all(), many=True, required=False, write_only=True,
    )


class ProductAttributeAdminSerializer(BaseProductAttributeAdminSerializer):
    class Meta:
        model = models.ProductAttribute
        fields = "__all__"
        extra_kwargs ={
            "require": {"write_only": True},
            "slug": {"write_only": True},
        }


class ProductAttributeDetailAdminSerializer(BaseProductAttributeAdminSerializer):
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


class BaseProductClassAdminSerializer(serializers.ModelSerializer):
    bases = serializers.PrimaryKeyRelatedField(
        queryset=models.ProductClass.objects.all(),
        many=True,
        required=False,
        write_only=True
    )


class ProductClassAdminSerializer(BaseProductClassAdminSerializer):
    class Meta:
        model = models.ProductClass
        fields = "__all__"
        extra_kwargs = {
            "metadata": {"write_only": True},
            "slug": {"write_only": True},
        }


class ProductClassDetailAdminSerializer(BaseProductClassAdminSerializer):
    class Meta:
        model = models.ProductClass
        fields = "__all__"

    def to_representation(self, instance):
        representaion = super().to_representation(instance)
        bases = []
        for product_class in instance.bases.only("pk", "title", "abstract"):
            bases.append({"pk": product_class.pk, "title": product_class.title, "abstract": product_class.abstract})
        representaion["bases"] = bases
        return representaion
