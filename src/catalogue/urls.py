from django.urls import path
from . import views


urlpatterns = [
    path("categories/", views.CategoryList.as_view()),
    path("category/<slug:slug>/", views.CategoryDetail.as_view()),
]
