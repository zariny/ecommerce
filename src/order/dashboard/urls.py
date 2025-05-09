from django.urls import path
from . import views


urlpatterns = [
    path("sales-overview/", views.SalesMetricView.as_view()),
]
