from rest_framework import serializers
from .. import models


class OrderSerializer(serializers.Serializer):
    date = serializers.DateTimeField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)