from django.db.models import functions, Sum
from rest_framework import generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from utils.permissions import AdminAndModelLevelPermission
from utils.authenticate import JWTCookiesBaseAuthentication
from utils.filters import DateRangeFilterSet
from .. import models
from . import serializers


class SalesMetricFilterSet(DateRangeFilterSet):
    class Meta:
        field_name = "date_placed"


class SalesMetricView(generics.ListAPIView):
    authentication_classes = (JWTCookiesBaseAuthentication,)
    permission_classes = (AdminAndModelLevelPermission,)
    queryset = models.Order.objects.filter(status="complete")
    serializer_class = serializers.OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SalesMetricFilterSet

    def get(self, request, *args, **kwargs):
        filterset = self.filterset_class(data=request.GET, queryset=self.get_queryset(), request=request)

        if not filterset.is_valid():
            return Response(filterset.errors, status=400)

        proper_trunk = functions.TruncDay if filterset.delta <= 30 else functions.TruncMonth
        queryset = filterset.qs.annotate(
            date=proper_trunk("date_placed")
        ).values("date").annotate(
            total=Sum("total_excl_tax")
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
