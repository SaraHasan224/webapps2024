from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect

from payapp.helpers import assign_wallet_on_registration
from payapp.models import Profile, Currency, Wallet
from .forms import RegistrationForm
from django.contrib import messages, auth
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user


# Create your views here.

def page_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save user to the database
            _currency = Currency.objects.get(id=form.cleaned_data.get('currency'))
            form.currency = _currency
            # Create or update model user
            user = form.save(commit=False)
            user.save()

            # Create a UserProfile for the user
            user_profile, _ = Profile.objects.get_or_create(user=user)
            user_profile.currency = _currency
            user_profile.save()

            # Create a UserWallet for the transactions
            wallet = assign_wallet_on_registration(user, user_profile)
            print('wallet')
            print(wallet)
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


# USER


# TRANSACTIONS
def transactions(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('/show')
            except:
                pass
    else:
        form = EmployeeForm()
    return render(request, 'index.html', {'form': form})


def transactionShow(request):
    employees = Employee.objects.all()
    return render(request, "show.html", {'employees': employees})


def transactionEdit(request, id):
    employee = Employee.objects.get(id=id)
    return render(request, 'edit.html', {'employee': employee})


def transactionUpdate(request, id):
    employee = Employee.objects.get(id=id)
    form = EmployeeForm(request.POST, instance=employee)
    if form.is_valid():
        form.save()
        return redirect("/show")
    return render(request, 'edit.html', {'employee': employee})


def transactionDestroy(request, id):
    employee = Employee.objects.get(id=id)
    employee.delete()
    return redirect("/show")
