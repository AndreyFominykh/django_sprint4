from django.shortcuts import render


def about(request):
    """Страница о проекте"""
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    """Страница наши правила"""
    template = 'pages/rules.html'
    return render(request, template)


def page_not_found(request, exception):
    """страница для ошибки 404"""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Страница для ошибки 403"""
    return render(request, 'pages/403csrf.html', status=403)


def server_error_failure(request):
    """Страница для ошибки 500"""
    return render(request, 'pages/500.html', status=500)
