from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
# request -> response
# Request handler
# Action

def index(request):
    return HttpResponse('My application frontend')


def page_error_400(request, exception):
    return render(request, '400.html', status=400)


def page_error_403(request, exception):
    return render(request, '403.html', status=403)


def page_error_404(request, exception):
    return render(request,'404.html', status=404)


def page_error_500(request):
    return render(request, '500.html', status=500)


def page_error_503(request, exception):
    return render(request, '503.html')
