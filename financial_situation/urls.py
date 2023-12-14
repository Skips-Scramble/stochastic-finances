from django.urls import path

from . import views

app_name = "financial_situation"

urlpatterns = [
    path("", views.test_new_form, name="test_new_form"),
    path(
        "financial_situation/",
        views.add_financial_situation,
        name="add_financial_situation",
    ),
    path("<int:pk>/edit/", views.edit, name="edit"),
]
