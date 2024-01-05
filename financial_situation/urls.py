from django.urls import path

from . import views

app_name = "financial_situation"

urlpatterns = [
    path("", views.test_new_form, name="test_new_form"),
    path("general/", views.general_inputs_view, name="general_inputs_view"),
    path("savings/", views.savings_inputs_view, name="savings_inputs_view"),
    path("payments/", views.payments_inputs_view, name="payments_inputs_view"),
    path("retirement/", views.retirement_inputs_view, name="retirement_inputs_view"),
    path("rates/", views.rates_inputs_view, name="rates_inputs_view"),
    path("calculation/", views.calculation, name="calculation"),
    path(
        "financial_situation/",
        views.add_financial_situation,
        name="add_financial_situation",
    ),
    path("<int:pk>/edit/", views.general_inputs_edit, name="general_inputs_edit"),
]
