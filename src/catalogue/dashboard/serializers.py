from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .. import models


class BaseCategoryAdminSerializer(serializers.ModelSerializer):
    positions = [("root", "Root"), ("first_child_of", "First Child Of"), ("after", "After"), ("before", "Before")]
    position = serializers.ChoiceField(choices=positions, default=positions[0][0], write_only=True, label="Position")
    relative_to = serializers.PrimaryKeyRelatedField(
        queryset=models.Category.objects.all(),
        write_only=True,
        many=False,
        required=False,
        label="Relative to"
    )

    def update(self, instance, validated_data):
        position = validated_data.pop("position", None)
        return instance
        ...


    def create(self, validated_data):
        position = validated_data.pop("position")
        if position == "root":
            instance = models.Category.add_root(**validated_data)
        else:
            relative_node = validated_data.pop("relative_to", None)
            if relative_node is None:
                raise ValidationError({"relative_to": ["This field is required."]})
            match position:
                case "first_child_of":
                    instance = relative_node.add_child(**validated_data)
                case "after":
                    instance = relative_node.add_sibling(pos="right", **validated_data)
                case "before":
                    instance = relative_node.add_sibling(pos="left", **validated_data)
        return instance


class CategoryAdminSerializer(BaseCategoryAdminSerializer):
    class Meta:
        model = models.Category
        # fields = ("pk", "name", "is_public", "ancestors_are_public", "is_root", "depth", "path") #unable to resolve type hint for
        # function "is_root". Consider using a type hint or @extend_schema_field. Defaulting to string.

        fields = (
            "pk", "name", "slug", "is_public", "ancestors_are_public", "is_root", "description", "meta_title",
            "meta_description", "metadata", "updated_at", "background", "background_caption", "position", "relative_to",
        )
        extra_kwargs = {
            "slug": {"write_only": True},
            "description": {"write_only": True},
            "meta_title": {"write_only": True},
            "meta_description": {"write_only": True},
            "metadata": {"write_only": True},
            "background": {"write_only": True},
            "background_caption": {"write_only": True},
        }

    def to_representation(self, instance):
        representaion = super().to_representation(instance)
        children = []
        for child in instance.get_children().only("pk", "name", "is_public", "ancestors_are_public", "numchild"):
            children.append(
                {
                    "pk": child.pk,
                    "name": child.name,
                    "is_public": child.is_public,
                    "ancestors_are_public": child.ancestors_are_public,
                    "numchild": child.numchild
                }
            )
        representaion["children"] = children
        return representaion


class CategoryDeatilAdminSerializer(BaseCategoryAdminSerializer):

    class Meta:
        model = models.Category
        # exclude = ("path", "depth", "numchild")
        fields = (
            "pk", "name", "slug", "full_name", "is_public", "ancestors_are_public", "description", "meta_title",
            "meta_description", "metadata", "updated_at", "background", "background_caption", "position", "relative_to",
        )
        # extra_kwargs = {
        #     "depth": {"write_only": True},
        #     "path": {"write_only": True}
        # }
