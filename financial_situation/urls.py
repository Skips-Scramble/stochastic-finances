from django.urls import path

from . import views

app_name = "financial_situation"

urlpatterns = [
    path("calculation/", views.calculation, name="calculation"),
]
