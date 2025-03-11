from django.urls import path, include
from . import views


urlpatterns = [
    path("categories/", views.CategoryList.as_view()),
    path("category/<slug:slug>/", views.CategoryDetail.as_view()),

    path("admin/", include("catalogue.dashboard.urls"))
]
