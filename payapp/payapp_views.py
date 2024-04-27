from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from payapp.forms import UserForm, WalletTopupForm
from payapp.helpers import get_exchange_rate, percentage, log_transaction, transaction_status
from payapp.models import Profile, Wallet, Transaction, Payee, Currency
from register.decorators import allowed_users, admin_only


def index(request):
    context = {
        "page_title": "EasyTransact"
    }
    return render(request, 'payapps/home.html', context)


@login_required(login_url='auth:login')
def dashboard(request):
    profile = Profile.objects.get(user=request.user)
    wallet = Wallet.objects.get(user_id=request.user.id)
    payees = []
    # payees = get_object_or_404(Payee, sender=request.user)
    print('my_payees')
    print(payees)
    transactions = []
    # transactions = get_object_or_404(Transaction, sender=request.user)
    print('transactions')
    print(transactions)
    context = {
        "page_title": "Dashboard",
        'profile': profile,
        "payees": payees,
        "transactions": transactions,
        'wallet': wallet
    }
    return render(request, 'payapps/dashboard.html', context)


# Profile

@login_required(login_url='auth:login')
# @allowed_users(allowed_roles=['customer'])
def app_profile(request):
    context = {
        "page_title": "App Profile"
    }
    return render(request, 'payapps/profile/app-profile.html', context)


# Admin Management

@login_required(login_url='auth:login')
def users_list(request):
    context = {
        "page_title": "Users",
        'page_main_heading': "Users List",
        "page_main_description": "Manage users of your application",
        "show_add_new_btn": True,
    }
    return render(request, 'payapps/users/index.html', context)


def users_show(request):
    user = User.objects.all()
    return render(request, "payapps/users/show.html", {'user': user})


@login_required(login_url='auth:login')
# @admin_only
def users_add(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # Cleaned data
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password1 = form.cleaned_data.get("password1")
            password2 = form.cleaned_data.get("password2")
            # curr = form.cleaned_data.get("currency")
            # print(curr)
            # currency = Currency.objects.get(iso_code=curr)
            # print(currency)
            # Additional data cleaning and processing if needed
            user = User.objects.create_user(
                first_name=form.cleaned_data.get("first_name"),
                last_name=form.cleaned_data.get("last_name"),
                username=form.cleaned_data.get("username"),
                email=form.cleaned_data.get("email"),
                password=form.cleaned_data.get("password1"),
            )
            # Profile.objects.create(
            #     user=user,
            #     currency_id=currency.id).save()
            try:
                # Save user to the database
                user = form.save()
                return redirect('/show')
            except:
                pass
    else:
        form = UserForm()

    context = {
        "page_title": "Users",
        'parent_module': "User",
        'child_module': "Add New",
        'form_title': "Add New User Form",
        'form': form
    }
    return render(request, 'payapps/users/add.html', context)


@login_required(login_url='auth:login')
@admin_only
def users_edit(request, id):
    context = {
        "page_title": "Users",
        'parent_module': "User",
        'child_module': "Edit New",
        'form_title': "Edit User Form",
        'id': id,
    }
    if request.method == "POST":
        users = User.objects.get(id=id)
        form = UserForm(request.POST, instance=users)
        if form.is_valid():
            form.save()
            return redirect("/show")
    else:
        user = User.objects.get(id=id)
        context['user'] = user
        return render(request, 'payapps/users/edit.html', context)


@login_required(login_url='auth:login')
@admin_only
def users_destroy(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return redirect("/show")


@login_required(login_url='auth:login')
@admin_only
def roles_list(request):
    context = {
        "page_title": "Roles",
        'page_main_heading': "Roles List",
        "page_main_description": "Manage roles in your application",
        "show_add_new_btn": True
    }
    return render(request, 'payapps/roles/index.html', context)


@login_required(login_url='auth:login')
@admin_only
def roles_add(request):
    context = {
        "page_title": "Roles",
        'parent_module': "Roles",
        'child_module': "Add New",
        'form_title': "Add New Roles Form"
    }
    return render(request, 'payapps/roles/add.html', context)


@login_required(login_url='auth:login')
@admin_only
def roles_edit(request, id):
    context = {
        "page_title": "Roles",
        'parent_module': "Roles",
        'child_module': "Edit New",
        'form_title': "Edit Roles Form"
    }
    return render(request, 'payapps/roles/edit.html', context)


@login_required(login_url='auth:login')
@admin_only
def permission_list(request):
    context = {
        "page_title": "Permissions",
        'page_main_heading': "Permissions List",
        "page_main_description": "Manage permissions for your application",
        "show_add_new_btn": True
    }
    return render(request, 'payapps/permissions/index.html', context)


@login_required(login_url='auth:login')
@admin_only
def permission_add(request):
    context = {
        "page_title": "Permissions",
        'parent_module': "Permission",
        'child_module': "Add New",
        'form_title': "Add New Permission Form"
    }
    return render(request, 'payapps/permissions/add.html', context)


@login_required(login_url='auth:login')
@admin_only
def permissions_edit(request, id):
    context = {
        "page_title": "Permission",
        'parent_module': "Permission",
        'child_module': "Edit New",
        'form_title': "Edit Permission Form"
    }
    return render(request, 'payapps/roles/edit.html', context)


# Transaction


@login_required(login_url='auth:login')
def transaction_history(request):
    context = {
        "page_title": "Transaction History",
        "page_main_heading": "Wallet Transaction History",
        "page_main_description": "Easily add view, your wallet transaction history"
    }
    return render(request, 'payapps/payment/transaction-history.html', context)


# Topup


@login_required(login_url='auth:login')
@allowed_users(allowed_roles=['customer'])
def topup(request):
    if request.method == "POST":
        form = WalletTopupForm(request.POST)
        if form.is_valid():
            # Cleaned data
            selected_currency = form.cleaned_data.get("requested_currency")
            amount = form.cleaned_data.get("amount")
            currency = Currency.objects.get(id=selected_currency)
            try:
                # Find user wallet first
                wallet = Wallet.objects.get(user_id=request.user.id)
                selected_currency = currency.iso_code
                base_currency = wallet.currency.iso_code
                # Check user base currency and convert the amount
                if selected_currency != base_currency:
                    conversion = get_exchange_rate(base_currency, amount, selected_currency, request.user.id)
                    wallet_amt = conversion.get("converted_amt")
                else:
                    wallet_amt = amount

                my_wallet_amt = wallet.amount

                updated_wallet_amount = float(my_wallet_amt)+float(wallet_amt)
                withdrawal_limit = percentage(10, updated_wallet_amount)

                try:
                    wallet.amount = updated_wallet_amount
                    wallet.withdrawal_limit = updated_wallet_amount - withdrawal_limit
                    wallet.save()
                except Exception as e:
                    print(f"Wallet Error: {e}")
                transaction_log = {'sender_id': request.user.id, "sender_curr_id": wallet.currency.id,
                                   'sender_prev_bal': my_wallet_amt, 'sender_cur_bal': updated_wallet_amount,
                                   'receiver_id': request.user.id, 'receiver_curr_id': currency.id,
                                   'receiver_prev_bal': my_wallet_amt, 'receiver_cur_bal': updated_wallet_amount,
                                   'amount_requested': amount, 'comment': "Topup my wallet balance",
                                   'amount_sent': wallet_amt,
                                   'status': 1}
                log_transaction(transaction_log)

                return redirect('payapp:my-wallet')
            except Exception as e:
                return f"Error: {e}"
        return redirect('payapp:my-wallet')
    else:
        form = WalletTopupForm()
    context = {
        "page_title": "Top up",
        "page_main_heading": "Wallet Top up",
        "page_main_description": "Easily add funds, manage balance, and top up wallet",
        'parent_module': "Wallet",
        'child_module': "Top up",
        'form_title': "Wallet Top up",
        'form': form
    }
    return render(request, 'payapps/payment/wallet-topup.html', context)


@login_required(login_url='auth:login')
@allowed_users(allowed_roles=['customer'])
def my_payees(request):
    context = {
        "page_title": "My Payees",
        "page_main_heading": "Manage My Payees",
        "page_main_description": "Conveniently view your payees and request payments from them"
    }
    return render(request, 'payapps/payment/payees.html', context)


@login_required(login_url='auth:login')
@allowed_users(allowed_roles=['customer'])
def my_wallet(request):
    wallet = Wallet.objects.get(user_id=request.user.id)
    context = {
        "page_title": "My Wallet",
        "page_main_heading": "Wallet Top up",
        "page_main_description": "Conveniently view your wallet",
        'wallet': wallet
    }
    return render(request, 'payapps/payment/wallet.html', context)


@login_required(login_url='auth:login')
@allowed_users(allowed_roles=['customer'])
def create_invoices(request):
    context = {
        "page_title": "Create Invoices"
    }
    return render(request, 'payapps/create-invoices.html', context)
