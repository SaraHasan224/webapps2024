from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegistrationForm
from django.contrib.auth import login, logout, authenticate


# Create your views here.

def index(request):
    return HttpResponse('Hello World')


def page_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('payapp:dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'registration/sign_up.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('/')


def page_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Incorrect username or password')

    context = {}
    return render(request, 'registration/login.html', context)


def page_forgot_password(request):
    return render(request, 'auth/pages/page-forgot-password.html')
