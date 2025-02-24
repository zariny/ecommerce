from django.urls import path
from .administration.urls import urlpatterns as admin_urlpatterns
from . import views


urlpatterns = [
    path("products/", views.ProductList.as_view()),
    path("product/<slug:slug>", views.ProductDetail.as_view()),
] + admin_urlpatterns
