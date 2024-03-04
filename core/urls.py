from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home_page, name="home"),
    path("alerts/", views.alerts_page, name="alerts"),
    path("buttons/", views.buttons_page, name="buttons"),
    path("blank/", views.blank_page, name="blank"),
    path("test_base/", views.test_base, name="test_base"),
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html", authentication_form=LoginForm
        ),
        name="login",
    ),
]
