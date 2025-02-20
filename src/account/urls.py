from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.UserAuthenticationView.as_view()),
]
