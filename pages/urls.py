from django.urls import path

from .views import (
    AlertsPageView,
    BlankPageView,
    ButtonsPageView,
    HomePageView,
    general_inputs_create,
    general_inputs_dashboard,
    general_inputs_delete,
    general_inputs_edit,
)

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
]
