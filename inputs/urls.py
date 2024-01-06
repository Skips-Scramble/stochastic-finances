from django.urls import path

from . import views

app_name = "inputs"

urlpatterns = [
    path("general/", views.general_inputs_dashboard, name="general_inputs_dashboard"),
    path("general/create/", views.general_inputs_create, name="general_inputs_create"),
    path(
        "general/<int:pk>/edit/", views.general_inputs_edit, name="general_inputs_edit"
    ),
    path("savings/", views.savings_inputs_dashboard, name="savings_inputs_dashboard"),
    path("savings/create/", views.savings_inputs_create, name="savings_inputs_create"),
    path(
        "savings/<int:pk>/edit/", views.savings_inputs_edit, name="savings_inputs_edit"
    ),
]
