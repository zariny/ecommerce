from django.urls import path
from . import views


urlpatterns = [
    path("categories/", views.CategoryAdminView.as_view()),
    # path("category/<int:pk>/", views.CategoryDetailAdminView.as_view()),
]
