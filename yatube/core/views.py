from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'core/404.html',
                {'path': request.path}, status = 404)  # HTTPStatus.NOT_FOUND


def server_error(request):
    return render(request, "core/500.html",
                status = 500) # HTTPStatus.INTERNAL_SERVER_ERROR


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html',
                status = 403) # HTTPStatus.FORBIDDEN