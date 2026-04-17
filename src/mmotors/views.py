from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, "index.html")


def error_400(request, exception):
    return render(request, "400.html", status=400)


def error_403(request, exception):
    return render(request, "403.html", status=403)


def error_404(request, exception):
    return render(request, "404.html", status=404)


def error_500(request):
    return render(request, "500.html", status=500)

from django.core.exceptions import PermissionDenied

def test403(request):
    raise PermissionDenied