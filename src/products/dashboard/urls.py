from django.urls import path
from . import views


urlpatterns = [
    path("products/", views.ProductAdminView.as_view()),
    path("product/<int:pk>/", views.ProductDetailAdminView.as_view()),
    path("attributes/", views.ProductAttributeAdminView.as_view()),
    path("attribute/<int:pk>/", views.ProductAttributeDetailAdminView.as_view()),
    path("productclasses/", views.ProductClassAdminView.as_view()),
    path("productclass/<int:pk>/", views.ProductClassDetailAdminView.as_view()),
    path("product-count/", views.ProductCountView.as_view()),
]
