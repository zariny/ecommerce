from django.urls import path, include
from . import views


urlpatterns = [
    path("products/", views.ProductList.as_view()),
    path("product/<slug:slug>", views.ProductDetail.as_view()),
    path("admin/", include("products.dashboard.urls")),
]
