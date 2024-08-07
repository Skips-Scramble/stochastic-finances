from django.urls import path

from .views import (AlertsPageView, BlankPageView, ButtonsPageView,
                    HomePageView, calculations, general_inputs_create,
                    general_inputs_dashboard, general_inputs_delete,
                    general_inputs_edit, payments_inputs_create,
                    payments_inputs_dashboard, payments_inputs_delete,
                    payments_inputs_edit, rates_inputs_create,
                    rates_inputs_dashboard, rates_inputs_delete,
                    rates_inputs_edit, retirement_inputs_create,
                    retirement_inputs_dashboard, retirement_inputs_delete,
                    retirement_inputs_edit, savings_inputs_create,
                    savings_inputs_dashboard, savings_inputs_delete,
                    savings_inputs_edit)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("alerts/", AlertsPageView.as_view(), name="alerts"),
    path("buttons/", ButtonsPageView.as_view(), name="buttons"),
    path("blank/", BlankPageView.as_view(), name="blank"),
    path("general/", general_inputs_dashboard, name="general_inputs_dashboard"),
    path("general/create/", general_inputs_create, name="general_inputs_create"),
    path("general/<int:pk>/edit/", general_inputs_edit, name="general_inputs_edit"),
    path(
        "general/<int:pk>/delete/",
        general_inputs_delete,
        name="general_inputs_delete",
    ),
    path("savings/", savings_inputs_dashboard, name="savings_inputs_dashboard"),
    path("savings/create/", savings_inputs_create, name="savings_inputs_create"),
    path("savings/<int:pk>/edit/", savings_inputs_edit, name="savings_inputs_edit"),
    path(
        "savings/<int:pk>/delete/",
        savings_inputs_delete,
        name="savings_inputs_delete",
    ),
    path(
        "payments/",
        payments_inputs_dashboard,
        name="payments_inputs_dashboard",
    ),
    path(
        "payments/create/",
        payments_inputs_create,
        name="payments_inputs_create",
    ),
    path(
        "payments/<int:pk>/edit/",
        payments_inputs_edit,
        name="payments_inputs_edit",
    ),
    path(
        "payments/<int:pk>/delete/",
        payments_inputs_delete,
        name="payments_inputs_delete",
    ),
    path(
        "retirement/",
        retirement_inputs_dashboard,
        name="retirement_inputs_dashboard",
    ),
    path(
        "retirement/create/",
        retirement_inputs_create,
        name="retirement_inputs_create",
    ),
    path(
        "retirement/<int:pk>/edit/",
        retirement_inputs_edit,
        name="retirement_inputs_edit",
    ),
    path(
        "retirement/<int:pk>/delete/",
        retirement_inputs_delete,
        name="retirement_inputs_delete",
    ),
    path("rates/", rates_inputs_dashboard, name="rates_inputs_dashboard"),
    path("rates/create/", rates_inputs_create, name="rates_inputs_create"),
    path(
        "rates/<int:pk>/edit/",
        rates_inputs_edit,
        name="rates_inputs_edit",
    ),
    path(
        "rates/<int:pk>/delete/",
        rates_inputs_delete,
        name="rates_inputs_delete",
    ),
    path("calculations", calculations, name="calculations"),
]
