from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = 'pages/home.html'

class AlertsPageView(TemplateView):
    template_name = 'pages/alerts.html'

class ButtonsPageView(TemplateView):
    template_name = 'pages/buttons.html'

class BlankPageView(TemplateView):
    template_name = 'pages/blank.html'