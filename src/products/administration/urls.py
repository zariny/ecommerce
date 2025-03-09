from django.urls import path
from . import views


urlpatterns = [
    path("admin/products/", views.ProductAdminView.as_view()),
    path("admin/product/<int:pk>/", views.ProductDetailAdminView.as_view()),
    path("admin/attributes/", views.ProductAttributeAdminView.as_view()),
    path("admin/attribute/<int:pk>/", views.ProductAttributeDetailAdminView.as_view()),
    path("admin/productclasses/", views.ProductClassAdminView.as_view()),
    path("admin/productclass/<int:pk>/", views.ProductClassDetailAdminView.as_view()),
]
