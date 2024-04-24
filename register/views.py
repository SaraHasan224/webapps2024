from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.

def index(request):
    return HttpResponse('Hello World')


def page_register(request):
    return render(request, 'auth/pages/register.html')


def page_login(request):
    return render(request, 'auth/pages/login.html')


def page_forgot_password(request):
    return render(request, 'auth/pages/page-forgot-password.html')
