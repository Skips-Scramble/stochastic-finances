from django.urls import path

from .views import HomePageView, AlertsPageView, ButtonsPageView, BlankPageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('alerts/', AlertsPageView.as_view(), name='alerts'),
    path('buttons/', ButtonsPageView.as_view(), name='buttons'),
    path('blank/', BlankPageView.as_view(), name='blank'),
]
