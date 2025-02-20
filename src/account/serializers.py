from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError


User = get_user_model()

class UserAuthenticationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, required=True, style={"input_type": "password"})
