from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

import logging
from payapp.forms import UserForm, WalletTopupForm, RequestPaymentForm, MyPayeeForm, EditUserForm
from payapp.helpers import get_exchange_rate, percentage, log_transaction, transaction_status, \
    assign_wallet_on_registration
from payapp.models import Profile, Wallet, Transaction, Payee, Currency, CustomUser
from register.decorators import allowed_users, admin_only

logger = logging.getLogger(__name__)


def index(request):
    context = {
        "page_title": "EasyTransact"
    }
    return render(request, 'payapps/home.html', context)


@login_required(login_url='auth:login')
def dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser:
        profile = Profile.objects.get(user=request.user)
        try:
            wallet = Wallet.objects.get(user_id=request.user.id)
        except Wallet.DoesNotExist:
            wallet = None
        payees = []
        # payees = get_object_or_404(Payee, sender=request.user)
        transactions = []
        # transactions = get_object_or_404(Transaction, sender=request.user)
        context = {
            "page_title": "Dashboard",
            'profile': profile,
            "payees": payees,
            "transactions": transactions,
            'wallet': wallet
        }
        return render(request, 'payapps/dashboard.html', context)
    else:

        profile = Profile.objects.get(user=request.user)
        try:
            transactions = Transaction.objects.get()
        except Transaction.DoesNotExist:
            transactions = None

        group_name = 'customer'  # Assuming the group name is 'customer'
        group = Group.objects.get(name=group_name)
        context = {
            "page_title": "Dashboard",
            'stats': {
                'staff_users': CustomUser.objects.filter(is_staff=True, is_superuser=False).count(),
                'admin_users': CustomUser.objects.filter(is_superuser=True).count(),
                'customers': group.user_set.count()
            },
            "transactions": transactions,
        }
        return render(request, 'payapps/admin-dashboard.html', context)


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
        'users': CustomUser.objects.all(),
    }
    return render(request, 'payapps/admin/users/index.html', context)


@login_required(login_url='auth:login')
def users_show(request):
    user = CustomUser.objects.all()
    return render(request, "payapps/admin/users/show.html", {'selected_user': user})


@login_required(login_url='auth:login')
# @admin_only
def users_add(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user_group = Group.objects.get(id=role)
            try:
                # Save user to the database
                _currency = Currency.objects.get(id=form.cleaned_data.get('currency'))
                form.currency = _currency
                # Create or update model user
                user = form.save(commit=False)
                # Set password manually
                user.set_password(form.cleaned_data['password1'])
                user.save()

                # Create a UserProfile for the user
                user_profile, _ = Profile.objects.get_or_create(user=user)
                user_profile.currency = _currency
                user_profile.save()

                if user_group == 'customer':
                    # Create a UserWallet for the transactions
                    wallet = assign_wallet_on_registration(request, user, user_profile)
                    group = Group.objects.get(name='customer')
                    user.groups.add(group)
                else:
                    group = Group.objects.get(name=user_group.name)
                    user.groups.add(group)
                return redirect('payapp:users-list')
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
    return render(request, 'payapps/admin/users/add.html', context)


@login_required(login_url='auth:login')
# @admin_only

def users_edit(request, id):
    user = CustomUser.objects.get(id=id)

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():

            role = form.cleaned_data.get('role')
            currency = form.cleaned_data.get('currency')
            is_superuser = form.cleaned_data.get('is_superuser')
            is_staff = form.cleaned_data.get('is_staff')

            customer_group = Group.objects.get(name='customer')
            user_group = Group.objects.get(id=role)
            if user_group.id == customer_group.id and is_superuser:
                role = Group.objects.get(name='superadmin').id
            elif user_group.id == customer_group.id and is_staff:
                role = Group.objects.get(name='staff').id

            # Save user to the database
            _currency = Currency.objects.get(id=currency)

            # Create or update model user
            form.currency = _currency
            user = form.save(commit=False)
            user.save()

            # Create a UserProfile for the user
            user_profile, _ = Profile.objects.get_or_create(user_id=user.id)
            user_profile.currency = _currency
            user_profile.save()

            try:
                if user_group.id == customer_group.id:
                    try:
                        wallet = Wallet.objects.get(user_id=user.id)
                    except Wallet.DoesNotExist:
                        wallet = None

                    if wallet is None:
                        # Assign a UserWallet if not already assigned
                        assign_wallet_on_registration(request, user, user_profile)
                    group = Group.objects.get(name='customer')
                    user.groups.add(group)
                else:
                    group = Group.objects.get(id=user_group)
                    user.groups.add(group)
                return redirect('payapp:users-list')
            except Exception as e:
                return f"Error: {e}"
            return redirect('payapp:users-list')  # Redirect to user list page
    else:
        # Assuming 'group_id' is the field in the form where you want to select the group ID
        form = EditUserForm(instance=user, initial={'group_id': user.groups.all()[0].id})

    context = {
        "page_title": "Users",
        'parent_module': "User",
        'child_module': "@" + user.username,
        'form_title': "Edit User Form",
        'id': id,
        'form': form,
        'selected_user': user
    }
    return render(request, 'payapps/admin/users/edit.html', context)


# @login_required(login_url='auth:login')
# @admin_only
def users_destroy(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('payapp:users-list')  # Redirect to user list page after deletion
    context = {
        "page_title": "Users",
        'parent_module': "Users",
        'child_module': "@" + user.username,
        'form_title': "Delete User @" + user.username,
        'selected_user': user
    }
    return render(request, 'payapps/admin/users/delete.html', context)


# Transaction
@login_required(login_url='auth:login')
def transaction_history(request):
    if request.user.is_superuser:
        transaction = Transaction.objects.all()
    elif request.user.is_staff:
        transaction = Transaction.objects.all()
    else:
        transaction = Transaction.objects.filter(sender_id=request.user.id)
    context = {
        "page_title": "Transaction History",
        "page_main_heading": "Wallet Transaction History",
        "page_main_description": "Easily add view, your wallet transaction history",
        'transactions': transaction
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
                    conversion = get_exchange_rate(request, base_currency, amount, selected_currency, request.user.id)
                    wallet_amt = conversion.get("converted_amt")
                else:
                    wallet_amt = amount

                my_wallet_amt = wallet.amount

                updated_wallet_amount = float(my_wallet_amt) + float(wallet_amt)
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
def my_wallet(request):
    try:
        wallet = Wallet.objects.get(user_id=request.user.id)
    except Wallet.DoesNotExist:
        wallet = None
    context = {
        "page_title": "My Wallet",
        "page_main_heading": "Wallet Top up",
        "page_main_description": "Conveniently view your wallet",
        'wallet': wallet
    }
    return render(request, 'payapps/payment/wallet.html', context)


@login_required(login_url='auth:login')
@allowed_users(allowed_roles=['customer'])
def request_payment(request):
    if request.method == "POST":
        form = RequestPaymentForm(request.POST)
        if form.is_valid():
            # Cleaned data
            selected_currency = form.cleaned_data.get("currency")
            amount = form.cleaned_data.get("amount")
            receiver = form.cleaned_data.get("receiver")
            currency = Currency.objects.get(id=selected_currency)
            selected_currency = currency.iso_code
            try:
                # Find user wallet first
                profile = Profile.objects.get(user_id=request.user.id)
                base_currency = profile.currency.iso_code
                # Check user base currency and convert the amount
                if selected_currency != base_currency:
                    conversion = get_exchange_rate(request, base_currency, amount, selected_currency, request.user.id)
                    wallet_amt = conversion.get("converted_amt")
                else:
                    wallet_amt = amount

                # Check receiver base currency and convert the amount
                if selected_currency != base_currency:
                    conversion = get_exchange_rate(request, receiver.profile.currency.iso_code, amount, selected_currency,
                                                   receiver.user.id)
                    receiver_wallet_amt = conversion.get("converted_amt")
                else:
                    receiver_wallet_amt = amount

                wallet = Wallet.objects.get(user_id=request.user.id)
                my_wallet_amt = wallet.amount

                updated_wallet_amount = float(my_wallet_amt) + float(wallet_amt)
                withdrawal_limit = percentage(10, updated_wallet_amount)

                try:
                    wallet.amount = updated_wallet_amount
                    wallet.withdrawal_limit = updated_wallet_amount - withdrawal_limit
                    wallet.save()
                except Exception as e:
                    print(f"Wallet Error: {e}")

                transaction_log = {'sender_id': request.user.id, "sender_curr_id": profile.currency.id,
                                   'sender_prev_bal': my_wallet_amt, 'sender_cur_bal': updated_wallet_amount,
                                   'receiver': receiver, 'receiver_curr_id': receiver.currency.id,
                                   'receiver_prev_bal': receiver.wallet.amount,
                                   'receiver_cur_bal': receiver.wallet.amount - receiver_wallet_amt,
                                   'amount_requested': amount,
                                   'comment': f"Transfer from {request.user.username} to {receiver.username}",
                                   'amount_sent': receiver_wallet_amt,
                                   'status': 1}
                log_transaction(transaction_log)

                return redirect('payapp:my-wallet')
            except Exception as e:
                return f"Error: {e}"
        return redirect('payapp:my-wallet')
    else:
        form = RequestPaymentForm()
    context = {
        "page_title": "Request Payment",
        'parent_module': "Wallet",
        'child_module': "Request Payment",
        'form_title': "Request Payment",
        'form': form
    }
    return render(request, 'payapps/payment/request-payment.html', context)

@login_required(login_url='auth:login')
@allowed_users(allowed_roles=['customer'])
def request_payment_from_payee(request, request_id):
    user = CustomUser.objects.get(id=request_id)
    if request.method == "POST":
        form = RequestPaymentForm(request.POST)
        if form.is_valid():
            # Cleaned data
            selected_currency = form.cleaned_data.get("currency")
            amount = form.cleaned_data.get("amount")
            receiver = form.cleaned_data.get("receiver")
            currency = Currency.objects.get(id=selected_currency)
            selected_currency = currency.iso_code
            try:
                # Find user wallet first
                profile = Profile.objects.get(user_id=request.user.id)
                base_currency = profile.currency.iso_code
                # Check user base currency and convert the amount
                if selected_currency != base_currency:
                    conversion = get_exchange_rate(request, base_currency, amount, selected_currency, request.user.id)
                    wallet_amt = conversion.get("converted_amt")
                else:
                    wallet_amt = amount

                # Check receiver base currency and convert the amount
                if selected_currency != base_currency:
                    conversion = get_exchange_rate(request, receiver.profile.currency.iso_code, amount, selected_currency,
                                                   receiver.user.id)
                    receiver_wallet_amt = conversion.get("converted_amt")
                else:
                    receiver_wallet_amt = amount

                wallet = Wallet.objects.get(user_id=request.user.id)
                my_wallet_amt = wallet.amount

                updated_wallet_amount = float(my_wallet_amt) + float(wallet_amt)
                withdrawal_limit = percentage(10, updated_wallet_amount)

                try:
                    wallet.amount = updated_wallet_amount
                    wallet.withdrawal_limit = updated_wallet_amount - withdrawal_limit
                    wallet.save()
                except Exception as e:
                    print(f"Wallet Error: {e}")

                transaction_log = {'sender_id': request.user.id, "sender_curr_id": profile.currency.id,
                                   'sender_prev_bal': my_wallet_amt, 'sender_cur_bal': updated_wallet_amount,
                                   'receiver': receiver, 'receiver_curr_id': receiver.currency.id,
                                   'receiver_prev_bal': receiver.wallet.amount,
                                   'receiver_cur_bal': receiver.wallet.amount - receiver_wallet_amt,
                                   'amount_requested': amount,
                                   'comment': f"Transfer from {request.user.username} to {receiver.username}",
                                   'amount_sent': receiver_wallet_amt,
                                   'status': 1}
                log_transaction(transaction_log)

                return redirect('payapp:my-wallet')
            except Exception as e:
                return f"Error: {e}"
        return redirect('payapp:my-wallet')
    else:
        form = RequestPaymentForm(initial={'email_addr': user.email})
    context = {
        "page_title": "Request Payment",
        'parent_module': "Wallet",
        'child_module': "Request Payment",
        'form_title': "Request Payment",
        'form': form
    }
    return render(request, 'payapps/payment/request-payment.html', context)


# Transaction
@login_required(login_url='auth:login')
def payees_list(request):
    payees = Payee.objects.filter(sender_id=request.user.id)
    context = {
        "page_title": "Payee List",
        "page_main_heading": "Payee List",
        "page_main_description": "Easily add view, your payees",
        'payees': payees
    }
    return render(request, 'payapps/payment/payee-list.html', context)

@login_required(login_url='auth:login')
@allowed_users(allowed_roles=['customer'])
def my_payees(request):
    if request.method == "POST":
        form = MyPayeeForm(request.POST)
        if form.is_valid():
            print('form')
            print(form)
            # Cleaned data
            payee = form.cleaned_data.get("payee_email")
            print('payee')
            print(payee)

            # If you want to retrieve a single record and you're sure there's only one matching record:
            try:
                try:
                    payee_exists = CustomUser.objects.get(email=payee)
                except CustomUser.DoesNotExist:
                    payee_exists = None
                print('Create new payee if not exist')
                print('payee_exists')
                print(payee_exists)

                if payee_exists is None:
                    messages.error(request, 'The entered payee details doesn\'t exist in our system. Ask your friend '
                                            'to join PayGenius to transfer him payment.')
                    pass
                else:
                    try:
                        if request.user.id == payee_exists.id:
                            messages.error(request, 'Can\'t add self to as a payee.')
                            pass
                        else:
                            # If you want to retrieve a single record and you're sure there's only one matching record:
                            try:
                                is_already_added = Payee.objects.get(sender_id=request.user.id, payee_id=payee_exists.id)
                            except Payee.DoesNotExist:
                                is_already_added = None

                            if is_already_added:
                                messages.error(request, 'Payee already added.')
                            else:
                                print('Create new payee if not exist')
                                # Create new payee if not exist
                                payee = Payee.objects.create()
                                payee.sender = request.user
                                payee.payee = payee_exists
                                payee.save()
                                pass;
                    except Exception as e:
                        return f"Error: {e}"
            except User.DoesNotExist:
                payee_exists = None
    else:
        form = MyPayeeForm()

    context = {
        "page_title": "My Payees",
        "page_main_heading": "Manage My Payees",
        "page_main_description": "Conveniently view your payees and request payments from them",
        'parent_module': "Wallet",
        'child_module': "My Payees",
        'form_title': "My Payees",
        "form": form
    }
    return render(request, 'payapps/payment/payees.html', context)
