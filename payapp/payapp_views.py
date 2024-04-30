from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

import logging

from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from payapp.forms import UserForm, WalletTopupForm, RequestPaymentForm, MyPayeeForm, EditUserForm, \
    RequestPayeePaymentForm
from payapp.helpers import get_exchange_rate, percentage, log_transaction, assign_wallet_on_registration, \
    find_customer_by_email, random_with_n_digits, create_invoice
from payapp.models import Profile, Wallet, Transaction, Payee, Currency, CustomUser, Notification, Invoice
from register.decorators import allowed_users, admin_only
from timestampservice.timestampclient import TimestampClient

logger = logging.getLogger(__name__)

# Define a constant dictionary for user statuses
INVOICE_STATUS_OPTIONS = [
    ("0", "Draft"),
    ("1", "Sent"),
    ("2", "Processing"),
    ("3", "Processed"),
]
INVOICE_TRANSACTION_STATUS_OPTIONS = [
    ("1", "Paid"),
    ("0", "Not paid"),
]


def index(request):
    context = {
        "page_title": "EasyTransact"
    }
    return render(request, 'payapps/home.html', context)


@login_required
@transaction.atomic
def dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser:
        profile = Profile.objects.get(user=request.user)
        try:
            wallet = Wallet.objects.get(user_id=request.user.id)
        except Wallet.DoesNotExist:
            wallet = None

        try:
            payments = Invoice.objects.filter(sender_id=request.user.id).prefetch_related('receiver',
                                                                                          'transaction').order_by('-id').all()
        except Invoice.DoesNotExist:
            payments = None

        try:
            notifications = Notification.objects.filter(receiver_id=request.user.id).prefetch_related('sender',
                                                                                                      'invoice').order_by('-id').all()
        except Notification.DoesNotExist:
            notifications = None

        payees = []
        try:
            transactions = Transaction.objects.filter(sender=request.user).order_by('-id').values()
        except Transaction.DoesNotExist:
            transactions = None

        # transactions = get_object_or_404(Transaction, sender=request.user)
        print(payments)
        context = {
            "page_title": "Dashboard",
            'profile': profile,
            "payees": payees,
            "transactions": transactions,
            'payments': payments,
            'wallet': wallet,
            'notifications': notifications,
            'notification_count': notifications.count(),
            'invoice_status': INVOICE_STATUS_OPTIONS,
            'invoice_transaction_status': INVOICE_TRANSACTION_STATUS_OPTIONS,
        }
        return render(request, 'payapps/dashboard.html', context)
    else:
        try:
            transactions = Transaction.objects.get().order_by('-id').all()
        except Transaction.DoesNotExist:
            transactions = None

        group_name = 'customer'  # Assuming the group name is 'customer'
        group = Group.objects.get(name=group_name)
        context = {
            "page_title": "Dashboard",
            'stats': {
            },
            "transactions": transactions,
        }
        return render(request, 'payapps/admin-dashboard.html', context)


# Profile

@login_required
@transaction.atomic
# @allowed_users(allowed_roles=['customer'])
def app_profile(request):
    context = {
        "page_title": "App Profile"
    }
    return render(request, 'payapps/profile/app-profile.html', context)


# Admin Management

@login_required
@transaction.atomic
def users_list(request):
    context = {
        "page_title": "Users",
        'page_main_heading': "Users List",
        "page_main_description": "Manage users of your application",
        "show_add_new_btn": True,
        'users': CustomUser.objects.all().order_by('-id'),
    }
    return render(request, 'payapps/admin/users/index.html', context)


@login_required
@transaction.atomic
def users_show(request):
    user = CustomUser.objects.filter(id=request.user)
    return render(request, "payapps/admin/users/show.html", {'selected_user': user})


@login_required
@transaction.atomic
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
            except:
                pass
            return redirect('users-list')
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


@login_required
@transaction.atomic
@user_passes_test(lambda u: u.is_superuser, login_url='auth:login')
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
            except Exception as e:
                return f"Error: {e}"
        return redirect('users-list')  # Redirect to user list page
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


@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='auth:login')
@transaction.atomic
def users_destroy(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('users-list')  # Redirect to user list page after deletion


# Transaction
@login_required
@transaction.atomic
def transaction_history(request):
    if request.user.is_superuser:
        transaction = Transaction.objects.all().order_by('-id').values()
    elif request.user.is_staff:
        transaction = Transaction.objects.all().order_by('-id').values()
    else:
        transaction = Transaction.objects.filter(sender=request.user).order_by('-id').values()

    context = {
        "page_title": "Transaction History",
        "page_main_heading": "Wallet Transaction History",
        "page_main_description": "Easily add view, your wallet transaction history",
        'transactions': transaction,
        'status': INVOICE_TRANSACTION_STATUS_OPTIONS
    }
    return render(request, 'payapps/payment/transaction-history.html', context)


# Topup


@login_required
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
# @transaction.atomic
def topup(request):
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


@login_required
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
# @transaction.atomic
@require_POST
def topup_wallet_request(request):
    print('---topup_wallet_request----')
    print(timezone.now())
    try:
        wallet = Wallet.objects.get(user_id=request.user.id)
    except Wallet.DoesNotExist:
        wallet = None

    if request.method == "POST":
        form = WalletTopupForm(request.POST)
        if form.is_valid():
            # Cleaned data
            selected_currency = form.cleaned_data.get("requested_currency")
            amount = form.cleaned_data.get("amount")
            currency = Currency.objects.get(id=selected_currency)
            try:
                # Find user wallet first
                wallet = wallet
                print('wallet')
                print(wallet)
                print(wallet.amount)
                selected_currency = currency.iso_code
                print('selected_currency')
                print(selected_currency)
                base_currency = wallet.currency.iso_code
                print('base_currency')
                print(base_currency)
                # Check user base currency and convert the amount
                if selected_currency != base_currency:
                    conversion = get_exchange_rate(request, selected_currency, amount, base_currency, request.user.id)
                    wallet_amt = conversion.get("converted_amt")
                else:
                    wallet_amt = amount
                updated_wallet_amount = float(wallet.amount) + float(wallet_amt)
                print('updated_wallet_amount')
                print(float(wallet.amount))
                print(float(wallet_amt))
                print(float(wallet.amount) + float(wallet_amt))
                print(updated_wallet_amount)
                withdrawal_limit = percentage(10, updated_wallet_amount)
                print('withdrawal_limit')
                print(withdrawal_limit)

                wallet = Wallet.objects.get(user_id=request.user.id)
                updated_wallet = wallet
                updated_wallet.amount = updated_wallet_amount
                updated_wallet.withdrawal_limit = updated_wallet_amount - (updated_wallet_amount * withdrawal_limit)
                updated_wallet = updated_wallet.save()

                print('-- wallet')
                print(wallet)
                print('updated wallet')
                print(updated_wallet)

                wallet_user = request.user.wallet_user
                print('updated wallet')
                print(wallet_user)
                transaction_log = {
                    'sender_id': request.user.id,
                    "sender_curr_id": wallet.currency.id,
                    'sender_prev_bal': wallet.amount,
                    'sender_cur_bal': updated_wallet_amount,
                    'receiver_id': request.user.id,
                    'receiver_curr_id': wallet.currency.id,
                    'receiver_prev_bal': wallet.amount,
                    'receiver_cur_bal': updated_wallet_amount,
                    'amount_requested': amount,
                    'comment': f"Topup my wallet balance with {currency.iso_code}{wallet_amt}",
                    'amount_sent': wallet_amt,
                    'requested_currency_id': currency.id,
                    'sent_currency_id': wallet.currency.id,
                    'status': 1
                }

                log_transaction(transaction_log)
            except Exception as e:
                print(f"log_transaction Error: {e}")
            print('final wallet')
            print(wallet.amount)
            return redirect('dashboard')
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


@login_required
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
# @transaction.atomic
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


@login_required
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
def payment_requests(request):
    payment_requests = Invoice.objects.filter(sender_id=request.user.id).prefetch_related('receiver',
                                                                                          'transaction').order_by('-id').all()
    context = {
        "page_title": "Payment requests",
        "page_main_heading": "Requested Payments",
        "page_main_description": "Seamless Requests, Swift Payments: Discover Payments Requested",
        'requests': payment_requests
    }
    return render(request, 'payapps/payment/payments-requested.html', context)


@login_required
@transaction.atomic
def action_payment_requests(request, invoice_no):
    try:
        invoice = Invoice.objects.get(invoice_no=invoice_no)
    except Invoice.DoesNotExist:
        invoice = None

    if invoice is None:
        return redirect('request-payment')
    print('invoice')
    print(invoice)

    # Check if the query parameter 'my_param' exists in the request
    if 'status' in request.GET:
        action = request.GET.get('status')
    else:
        action = None
    print(action)

    if request.method == 'POST':
        if action == '0':
            invoice.status = 4
            invoice.save()
            messages.error(request, 'Payment request has been rejected.')
        else:
            invoice.status = 2
            invoice = invoice.save()
            #
            # # Check user base currency and convert the amount as per receiver_currency
            # # and then deduct this transfer_amt from sender's wallet
            # if transaction_currency != receiver_currency:
            #     print('Check user base currency and convert the amount as per receiver_currency')
            #     print(receiver_currency, transfer_wallet_amt, transaction_currency, sender.id)
            #     transfer_amt = get_exchange_rate(request, receiver_currency, transfer_wallet_amt,
            #                                      transaction_currency, sender.id)
            #     print(transfer_amt)
            #     transfer_amt = transfer_amt.get("converted_amt")
            # else:
            #     # If transaction currency and reciever's wallet currency is same then no need to convert
            #     # amount
            #     transfer_amt = amount
            #
            # print('transfer_amt without exchange rate', transfer_amt)
            # print(request, receiver_currency.iso_code, amount, transaction_currency,
            #       receiver.id)
            #
            # # Deduct amount from sender wallet
            # sender_wallet = update_sender_wallet(sender_wallet, transfer_wallet_amt, 'subtract')
            # # Add amount to receiver wallet
            # receiver_wallet = update_sender_wallet(receiver, transfer_amt, 'subtract')
            #
            # # Update transaction log
            # transaction.sender_cur_bal = sender_wallet.amount
            # transaction.receiver_cur_bal = receiver_wallet.amount
            # transaction.amount_sent = transfer_amt
            # transaction.status = 1
            # transaction = transaction.save()
            # print('updated transaction')
            # print(transaction)
            #
            # if transaction.status == 1:
            #     invoice.status = 3
            #     invoice.save()
    else:
        return ('dashboard')


@login_required
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
# @transaction.atomic
def request_payment(request):
    if request.method == "POST":
        try:
            sender = request.user
            sender_profile = request.user.assigned_profile
            sender_currency = sender_profile.currency
            sender_wallet = Wallet.objects.get(user_id=sender.id)
            sender_wallet_amt = sender_wallet.amount

            form = RequestPaymentForm(request.POST)
            if form.is_valid():
                # Cleaned data
                receiver = form.cleaned_data.get("payee_email")
                transaction_currency = form.cleaned_data.get("currency")
                amount = form.cleaned_data.get("amount")

                transaction_currency = Currency.objects.get(id=transaction_currency)

                receiver = find_customer_by_email(receiver)
                receiver_profile = receiver.assigned_profile
                receiver_currency = receiver_profile.currency
                receiver_wallet = Wallet.objects.get(user_id=sender.id)
                receiver_wallet_amt = receiver_wallet.amount

                invoice_no = random_with_n_digits(15)
                transfer_wallet_amt = None

                if sender.id == receiver.id:
                    errors = 'Can\'t add self to as a payee.'
                    # Store errors in session
                    request.session['errors'] = errors
                    return redirect('request-payment')
                elif receiver is None:
                    errors = 'The entered payee details doesn\'t exist in our system. Ask your friend '
                    'to join PayGenius to transfer him payment.'
                    # Store errors in session
                    request.session['errors'] = errors
                    return redirect('request-payment')
                else:
                    # Add payee if not already added
                    try:
                        payee = Payee.objects.filter(sender=sender, payee=receiver)
                    except Invoice.DoesNotExist:
                        payee = None
                    if payee is None:
                        payee = Payee.objects.create()
                        payee.sender = sender
                        payee.payee = receiver
                        payee.save()
                        print('payee created')
                    print('payee')
                    print(payee)
                    # Check user base currency and convert the amount as per currency in which user want to transact the amount
                    # and then sender's wallet
                    try:
                        print('transaction_currency')
                        print(transaction_currency)
                        print('sender_currency')
                        print(sender_currency)
                        if transaction_currency.iso_code != sender_currency.iso_code:
                            amt_to_transfer = get_exchange_rate(request, receiver_currency.iso_code, amount,
                                                                transaction_currency.iso_code, sender.id)
                            transfer_wallet_amt = amt_to_transfer.get("converted_amt")
                        else:
                            # If transaction currency and reciever's wallet currency is same then no need to convert amount
                            transfer_wallet_amt = amount
                    except Exception as e:
                        print(f"Error: {e}")
                    print('transfer_wallet_amt')
                    print(transfer_wallet_amt)
                    # Create a unpaid transaction log with just sender details
                    # and extend it further on after transacting amt and update the transaction amt after deducting it from wallet
                    transaction_log = {
                        'sender_id': sender.id,
                        "sender_curr_id": transaction_currency.id,
                        'sender_prev_bal': sender_wallet_amt,
                        'sender_cur_bal': sender_wallet_amt,
                        'receiver': receiver,
                        'receiver_curr_id': receiver_currency.id,
                        'receiver_prev_bal': receiver_wallet_amt,
                        'receiver_cur_bal': receiver_wallet_amt,
                        'amount_requested': transfer_wallet_amt,
                        'comment': f"Transfer {transaction_currency.iso_code}{transfer_wallet_amt} from {sender.username} to {receiver.username}",
                        'amount_sent': transfer_wallet_amt,
                        'status': 0,
                        'requested_currency_id': transaction_currency.id,
                        'sent_currency_id': receiver_currency.id,
                    }
                    print('transaction_log')
                    print(transaction_log)
                    transaction = log_transaction(transaction_log)
                    invoice_data = {
                        'invoice_no': invoice_no,
                        'transaction_date': timezone.now().date(),
                        'transaction': transaction,
                        'transaction_status': 0,
                        'sender': sender,
                        'receiver': receiver,
                        'status': 0
                    }
                    invoice = create_invoice(invoice_data)
                    invoice.status = 1
                    invoice.save()

                    notification = Notification.objects.create()
                    notification.is_read = 0
                    notification.receiver = receiver
                    notification.sender = sender
                    notification.invoice = invoice
                    notification.save()
                    # Clear any existing error messages
                    messages.error(request, None)
                    messages.success(request, 'Payment request has been made to ' + receiver.username)
        except Exception as e:
            print(f"Transaction Error: {e}")
        return redirect('request-payment')
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


@login_required
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
def request_payment_from_payee(request, request_id):
    receiver = CustomUser.objects.get(id=request_id)

    print('request_payment_from_payee')
    print(request_id)
    print('receiver')
    print(receiver)

    if request.method == "POST":
        try:
            print('POST FORM')
            sender = request.user
            sender_profile = request.user.assigned_profile
            sender_currency = sender_profile.currency
            sender_wallet = Wallet.objects.get(user_id=sender.id)
            sender_wallet_amt = sender_wallet.amount

            form = RequestPayeePaymentForm(request.POST)
            try:
                if form.is_valid():
                    # Cleaned data
                    print('form.cleaned_data')
                    # Print or log the form data including the hidden field
                    print(form.cleaned_data)
                    transaction_currency = form.cleaned_data.get("currency")
                    amount = form.cleaned_data.get("amount")

                    transaction_currency = Currency.objects.get(id=transaction_currency)

                    receiver_profile = receiver.assigned_profile
                    receiver_currency = receiver_profile.currency
                    receiver_wallet = Wallet.objects.get(user_id=sender.id)
                    print('receiver_wallet: ', receiver_wallet)
                    receiver_wallet_amt = receiver_wallet.amount

                    invoice_no = random_with_n_digits(15)
                    transfer_wallet_amt = None

                    if receiver is None:
                        messages.error(request,
                                       'The entered payee details doesn\'t exist in our system. Ask your friend '
                                       'to join PayGenius to transfer him payment.')
                        pass
                    else:
                        print(sender.id == receiver.id)
                        if sender.id == receiver.id:
                            messages.error(request, 'Can\'t add self to as a payee.')
                        else:
                            try:
                                # Check user base currency and convert the amount as per currency in which user want to transact the amount
                                # and then sender's wallet
                                print('transaction_currency')
                                print(transaction_currency)
                                print('sender_currency')
                                print(sender_currency)
                                print(transaction_currency.iso_code, sender_currency.iso_code)
                                print(receiver_currency.iso_code)
                                print(amount)
                                print(transaction_currency.iso_code)
                                print(sender.id)
                                if transaction_currency.iso_code != sender_currency.iso_code:
                                    amt_to_transfer = get_exchange_rate(request, sender.iso_code, amount,
                                                                        transaction_currency.iso_code, sender.id)
                                    print(amt_to_transfer)
                                    print('amt_to_transfer')
                                    transfer_wallet_amt = 0
                                    # transfer_wallet_amt = amt_to_transfer.get("converted_amt")
                                    print(transfer_wallet_amt)
                                    print('transfer_wallet_amt')
                                else:
                                    # If transaction currency and reciever's wallet currency is same then no need to convert amount
                                    transfer_wallet_amt = amount
                            except Exception as e:
                                print(f"DD Error: {e}")

                            print(transfer_wallet_amt)
                            print('transfer_wallet_amt')
                            # Create a unpaid transaction log with just sender details and extend it further on after
                            # transacting amt and update the transaction amt after deducting it from wallet
                            receiver = CustomUser.objects.get(id=request_id)
                            receiver_profile = receiver.assigned_profile
                            receiver_currency = receiver_profile.currency
                            transaction_log = {
                                'sender_id': sender.id,
                                "sender_curr_id": transaction_currency.id,
                                'sender_prev_bal': sender_wallet_amt,
                                'sender_cur_bal': sender_wallet_amt,
                                'receiver': receiver,
                                'receiver_curr_id': receiver_currency.id,
                                'receiver_prev_bal': receiver_wallet_amt,
                                'receiver_cur_bal': receiver_wallet_amt,
                                'amount_requested': transfer_wallet_amt,
                                'comment': f"Transfer {transaction_currency.iso_code}{transfer_wallet_amt} from {sender.username} to {receiver.username}",
                                'amount_sent': transfer_wallet_amt,
                                'status': 0,
                                'requested_currency_id': transaction_currency.id,
                                'sent_currency_id': sender.id,
                            }
                            print('transaction_log')
                            print(transaction_log)
                            transaction = log_transaction(transaction_log)
                            print('transaction')
                            print(transaction)
                            print('created invoice')
                            invoice_data = {
                                'invoice_no': invoice_no,
                                'transaction_date': timezone.now().date(),
                                'transaction': transaction,
                                'transaction_status': 0,
                                'sender': sender,
                                'receiver': receiver,
                                'status': 1
                            }
                            print(invoice_data)
                            invoice = create_invoice(invoice_data)
                            print('invoice')
                            print(invoice)

                            print('Notification')
                            print('invoice_id=invoice.id')
                            print(invoice.id)
                            print(receiver)
                            print(sender)
                            try:
                                # notification = Notification.objects.get_or_create(invoice_id=invoice.id)
                                # notification.is_read = 0
                                # notification.receiver = receiver
                                # notification.sender = sender
                                # notification.invoice = invoice
                                # notification.save()
                                print('notification')
                                print('11665465')
                            except Exception as e:
                                print(f"notification Error: {e}")

                            messages.success(request, 'Payment request has been made to ' + receiver.username)
            except Exception as e:
                print(f"request-payment: {e}")
            return redirect('request-payment')
        except Exception as e:
            print(f"Transaction Error: {e}")
    else:
        form = RequestPayeePaymentForm(initial={'email_addr': receiver.email})
        if receiver.is_superuser:
            # Store form errors in the session
            request.session['form_errors'] = form.errors
            # Clear any existing error messages
            messages.error(request, None)
            messages.error(request, 'The entered payee details belongs to a restricted user.')
            return redirect('my-payee-list')
        elif receiver.is_staff == True:
            request.session['form_errors'] = form.errors
            # Clear any existing error messages
            messages.error(request, None)
            messages.error(request, 'The entered payee details belongs to a restricted user.')
            return redirect('my-payee-list')
        else:
            # Clear any existing error messages
            messages.error(request, None)
            context = {
                "page_title": "Request Payment",
                'parent_module': "Wallet",
                'child_module': "Request Payment",
                'form_title': "Request Payment",
                'receiver': receiver,
                'form': form,
            }
            return render(request, 'payapps/payment/request-payment.html', context)


@login_required
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
def delete_payee(request, request_id):
    print('request_id')
    print(request_id)
    receiver = CustomUser.objects.get(id=request_id)
    payee = Payee.objects.filter(sender=request.user, payee=receiver)
    payee.delete()
    return redirect('my-payee-list')


# Transaction
@login_required
@transaction.atomic
def payees_list(request):
    payees = Payee.objects.filter(sender_id=request.user.id)
    context = {
        "page_title": "Payee List",
        "page_main_heading": "Payee List",
        "page_main_description": "Easily add view, your payees",
        'payees': payees
    }
    return render(request, 'payapps/payment/payee-list.html', context)


@login_required
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
def my_payees(request):
    if request.method == "POST":
        form = MyPayeeForm(request.POST)
        if form.is_valid():
            # Cleaned data
            payee = form.cleaned_data.get("payee_email")

            # If you want to retrieve a single record and you're sure there's only one matching record:
            try:
                try:
                    payee_exists = CustomUser.objects.get(email=payee)
                except CustomUser.DoesNotExist:
                    payee_exists = None

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
                                is_already_added = Payee.objects.get(sender_id=request.user.id,
                                                                     payee_id=payee_exists.id)
                            except Payee.DoesNotExist:
                                is_already_added = None

                            if is_already_added:
                                messages.error(request, 'Payee already added.')
                            else:
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
