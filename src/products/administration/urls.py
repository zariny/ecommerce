from django.urls import path
from . import views


urlpatterns = [
    path("admin/products/", views.ProductListCreateAdmin.as_view()),
    path("admin/product/<int:pk>/", views.ProductRetrieveUpdateAdmin.as_view()),
    path("admin/attributes/", views.ProductAttributeListCreateAdmin.as_view()),
    path("admin/attribute/<int:pk>/", views.ProductAttributeDetailAdmin.as_view()),
]
