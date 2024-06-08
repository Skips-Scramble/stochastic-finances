from django.urls import path

from .views import (
    AlertsPageView,
    BlankPageView,
    ButtonsPageView,
    HomePageView,
    general_inputs_create,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("alerts/", AlertsPageView.as_view(), name="alerts"),
    path("buttons/", ButtonsPageView.as_view(), name="buttons"),
    path("blank/", BlankPageView.as_view(), name="blank"),
    path("general/", general_inputs_create, name="general"),
]
