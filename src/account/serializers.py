from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError


User = get_user_model()

class UserAuthenticationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, required=True, style={"input_type": "password"})


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, validators=(UniqueValidator(queryset=User.objects.all()),))
    password = serializers.CharField(max_length=128, required=True, style={"input_type": "password"})
    password_again = serializers.CharField(max_length=128, required=True, style={"input_type": "password"})

    def validate(self, attrs):
        if attrs["password"] != attrs["password_again"]:
            message = {"password": "password do not match", "password_again": "password do not match"}
            raise serializers.ValidationError(message)

        try:
            password_validation.validate_password(attrs["password"])
        except ValidationError as e:
            raise serializers.ValidationError({"password": str(e)})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(validated_data["email"], validated_data["password"])
        return user
