from django.urls import path
from . import views

urlpatterns = [
    path("admin/users/", views.UserListAdminView.as_view()),
    path("admin/user/<int:pk>/", views.UserDetailAdminView.as_view()),
]