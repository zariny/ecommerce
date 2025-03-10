from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class UserListAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("pk", "email", "is_staff", "is_active", "last_login")


class UserDetailAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)
