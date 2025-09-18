from django.urls import path
from . import views


urlpatterns = [
    path("trafic/", views.TraficAnalyzerView.as_view()),
]
