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


class UserRoleSerializer(serializers.Serializer):
    roles = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of roles assigned to the current admin user"
    )


class UserGrowthChartSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)
    date = serializers.DateTimeField(read_only=True)
    class Meta:
        model = User
        fields = ("date", 'count')
