from django.urls import path

from . import views

app_name = "inputs"

urlpatterns = [
    path("general/", views.general_inputs_dashboard, name="general_inputs_dashboard"),
    path("general/create/", views.general_inputs_create, name="general_inputs_create"),
    path(
        "general/<int:pk>/edit/", views.general_inputs_edit, name="general_inputs_edit"
    ),
    path(
        "general/<int:pk>/delete/",
        views.general_inputs_delete,
        name="general_inputs_delete",
    ),
    path("savings/", views.savings_inputs_dashboard, name="savings_inputs_dashboard"),
    path("savings/create/", views.savings_inputs_create, name="savings_inputs_create"),
    path(
        "savings/<int:pk>/edit/", views.savings_inputs_edit, name="savings_inputs_edit"
    ),
    path(
        "savings/<int:pk>/delete/",
        views.savings_inputs_delete,
        name="savings_inputs_delete",
    ),
    path(
        "payments/", views.payments_inputs_dashboard, name="payments_inputs_dashboard"
    ),
    path(
        "payments/create/", views.payments_inputs_create, name="payments_inputs_create"
    ),
    path(
        "payments/<int:pk>/edit/",
        views.payments_inputs_edit,
        name="payments_inputs_edit",
    ),
    path(
        "payments/<int:pk>/delete/",
        views.payments_inputs_delete,
        name="payments_inputs_delete",
    ),
]
