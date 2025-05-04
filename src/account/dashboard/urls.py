from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.UserListAdminView.as_view()),
    path("user/<int:pk>/", views.UserDetailAdminView.as_view()),
    path("myrole/", views.AdminUserRoleView.as_view()),
]
