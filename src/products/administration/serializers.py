from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework import serializers
from catalogue.models import Category
from .. import models
from typing import List
from ..exceptions import CycleInheritanceError
from ..models import ProductClassRelation, ProductClass


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

    # def validate_product_type(self, value):
    #     if value.abstract:
    #         raise RestValidationError("Abstract product type %s can not have any product." % value)
    #     return value


class ProductAdminSerializer(BaseProductAdminSerializer):
    attributes=None
    class Meta:
        model = models.Product
        exclude = ("attributes", "created_at")
        extra_kwargs = {
            "slug": {"write_only": True},
            "meta_title": {"write_only": True},
            "meta_description": {"write_only": True},
            "description": {"write_only": True},
            "metadata": {"write_only": True},
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
        write_only=True,
    )

    def update(self, instance, valiated_data):
        bases = valiated_data.pop("bases", [])
        try:
            for base in bases:
                validate_no_cycles(base_product_kls=base, sub_product_kls=instance)
        except CycleInheritanceError as e:
            raise RestValidationError({"bases": e.message})
        super().update(instance, valiated_data)
        instance.bases.set(bases)
        return instance

    def create(self, vliated_data):
        bases = vliated_data.pop("bases", [])
        instance = super().create(vliated_data)
        self.create_relaion(instance, bases)
        return instance

    def create_relaion(self, instance: ProductClass, bases: List[ProductClass]):
        relation_objects = list()
        for base in bases:
            relation_obj = models.ProductClassRelation(subclass=instance, base=base)
            try:
                relation_obj.cycle_relation_validation()
            except DjangoValidationError as e:
                raise RestValidationError({"bases": str(e)})
            relation_objects.append(relation_obj)
        models.ProductClassRelation.objects.bulk_create(relation_objects, batch_size=100)


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
