from django.urls import path

from . import views

app_name = "inputs"

urlpatterns = [
    path("get_started/", views.get_started, name="get_started"),
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
        "payments/",
        views.payments_inputs_dashboard,
        name="payments_inputs_dashboard",
    ),
    path(
        "payments/create/",
        views.payments_inputs_create,
        name="payments_inputs_create",
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
    path(
        "retirement/",
        views.retirement_inputs_dashboard,
        name="retirement_inputs_dashboard",
    ),
    path(
        "retirement/create/",
        views.retirement_inputs_create,
        name="retirement_inputs_create",
    ),
    path(
        "retirement/<int:pk>/edit/",
        views.retirement_inputs_edit,
        name="retirement_inputs_edit",
    ),
    path(
        "retirement/<int:pk>/delete/",
        views.retirement_inputs_delete,
        name="retirement_inputs_delete",
    ),
    path("rates/", views.rates_inputs_dashboard, name="rates_inputs_dashboard"),
    path("rates/create/", views.rates_inputs_create, name="rates_inputs_create"),
    path(
        "rates/<int:pk>/edit/",
        views.rates_inputs_edit,
        name="rates_inputs_edit",
    ),
    path(
        "rates/<int:pk>/delete/",
        views.rates_inputs_delete,
        name="rates_inputs_delete",
    ),
]
