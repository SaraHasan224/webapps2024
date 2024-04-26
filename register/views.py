from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .forms import RegistrationForm
from django.contrib import messages, auth
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .decorators import  unauthenticated_user

# Create your views here.

def index(request):
    return HttpResponse('Hello World')

@unauthenticated_user
def page_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Cleaned data
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password1 = form.cleaned_data.get("password1")
            password2 = form.cleaned_data.get("password2")
            currency = form.cleaned_data.get("currency")
            # Additional data cleaning and processing if needed

            # Save user to the database
            user = form.save()
            # Additional processing after user registration if needed
            login(request, user)

            group = Group.objects.get(name='customer')
            user.groups.add(group)
            messages.success(request, 'Your payapp account has been created.')

            return redirect('payapp:dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'registration/sign_up.html', {'form': form})


@login_required(login_url='auth:login')
def edit_profile(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('payapp:dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'payapps/profile/app-profile.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('auth:login')

# def logout_user(request):
#     if request.method == "POST":
#         logout(request)
#         return redirect('auth:login')
#     return render(request, 'registration/logout.html', context)
#


@unauthenticated_user
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



@unauthenticated_user
def page_forgot_password(request):
    return render(request, 'auth/pages/page-forgot-password.html')
