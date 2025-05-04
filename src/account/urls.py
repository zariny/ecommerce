from django.urls import path, include
from . import views


urlpatterns = [
    path("login/", views.UserAuthenticationView.as_view()),
    path("refresh/", views.TokenRefreshView.as_view()),
    path("register/", views.UserRegistrationView.as_view()),
    path("admin/", include("account.dashboard.urls"))
]
