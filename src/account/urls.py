from django.urls import path
from . import views
from .administration.urls import urlpatterns as admin_urlpatterns


urlpatterns = [
    path("login/", views.UserAuthenticationView.as_view()),
    path("refresh/", views.TokenRefreshView.as_view()),
    path("register/", views.UserRegistrationView.as_view()),
] + admin_urlpatterns
