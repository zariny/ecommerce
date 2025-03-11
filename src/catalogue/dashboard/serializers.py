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

    def move(self, instance, position, relative_to=None):
        if position == "root":
            if instance.is_root():
                return instance
            root_node = models.Category.get_root_nodes().first()
            if root_node is None:
                raise ValidationError({"position": ["Cannot move to root because no root nodes exist."]})
            instance.move(root_node, pos="last-sibling")
        else:
            if relative_to is None:
                raise ValidationError({"relative_to": ["This field is required when moving the category."]})
            elif position == "after":
                instance.move(relative_to, pos="right")
            elif position == "before":
                instance.move(relative_to, pos="left")
            elif position == "first_child_of":
                instance.move(target=relative_to, pos="first-child")

        instance.refresh_from_db()
        return instance

    def update(self, instance, validated_data):
        position = validated_data.pop("position", None)
        relative_to = validated_data.pop("relative_to", None)
        instance = super().update(instance, validated_data)
        if position is not None:
            self.move(instance, position, relative_to)
        return instance

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
        fields = (
            "pk", "name", "slug", "full_name", "is_public", "ancestors_are_public", "description", "meta_title",
            "meta_description", "metadata", "updated_at", "background", "background_caption", "position", "relative_to",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.is_root():
            position = "root"
            relative_to = dict()
        else:
            relative_node = instance.get_prev_sibling()
            if relative_node is None:  # it was the leftmost sibling.
                position = "first_child_of"
                relative_to = instance.get_parent()
                relative_to = {"pk": relative_to.pk, "name": relative_to.name, "is_public": relative_to.is_public}
            else:
                position = "after"
                relative_to = {"pk": relative_node.pk, "name": relative_node.name, "is_public": relative_node.is_public}

        representation["position"] = position
        representation["relative_to"] = relative_to
        return representation
