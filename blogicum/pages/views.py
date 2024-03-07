from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Страница о проекте"""

    template = 'pages/about.html'


class RulesView(TemplateView):
    """Страница наши правила"""

    template = 'pages/rules.html'


def page_not_found(request, exception):
    """страница для ошибки 404"""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Страница для ошибки 403"""
    return render(request, 'pages/403csrf.html', status=403)


def server_error_failure(request):
    """Страница для ошибки 500"""
    return render(request, 'pages/500.html', status=500)
