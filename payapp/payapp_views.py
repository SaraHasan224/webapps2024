from decimal import Decimal

from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

import logging

from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from payapp.forms import UserForm, WalletTopupForm, RequestPaymentForm, MyPayeeForm, EditUserForm, \
    RequestPayeePaymentForm
from payapp.helpers import get_exchange_rate, percentage, log_transaction, assign_wallet_on_registration, \
    find_customer_by_email, random_with_n_digits, create_invoice, get_timestamp
from payapp.models import Profile, Wallet, Transaction, Payee, Currency, CustomUser, Notification, Invoice, \
    RequestResponseLogs
from register.decorators import allowed_users, admin_only

logger = logging.getLogger(__name__)

# Define a constant dictionary for user statuses
INVOICE_STATUS_OPTIONS = [
    ("0", "Draft"),
    ("1", "Sent"),
    ("2", "Processing"),
    ("3", "Processed"),
]
ACTIONS_OPTIONS = [
    ("0", "Void"),
    ("1", "Credit"),
    ("2", "Debit"),
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
@csrf_protect
@transaction.atomic
def dashboard(request):
    print('I am user')
    profile = Profile.objects.get(user=request.user)

    payments = None
    wallet = None
    notifications = None
    payees = []
    stats = None
    if not request.user.is_staff and not request.user.is_superuser:
        try:
            transactions = Transaction.objects.filter(sender=request.user).order_by('-id').prefetch_related(
                'receiver').values()
        except Transaction.DoesNotExist:
            transactions = None

        try:
            payments = Invoice.objects.filter(sender_id=request.user.id).prefetch_related('receiver',
                                                                                          'transaction').order_by(
                '-id').all()
        except Invoice.DoesNotExist:
            payments = None
        try:
            wallet = Wallet.objects.get(user_id=request.user.id)
        except Wallet.DoesNotExist:
            wallet = None
            # Query to add up received_amount where sender and receiver are different
        total_received_amount = Transaction.objects.filter(sender=F('receiver'), receiver_id=request.user.id).aggregate(record_count=Count('id'))
        stats = {
            'c': {
                'title': 'Payments Requested',
                'value': payments.count(),
            },
            'b': {
                'title': 'Pending Payment Action',
                'value': f"{profile.currency.iso_code} {total_received_amount['record_count']}"
            },
            'a': {
                'title': 'My Wallet',
                'value': f"{profile.currency.iso_code} {wallet.amount}"
            },
        }
    else:
        try:
            transactions = Transaction.objects.all().prefetch_related(
                'receiver', 'sender').order_by('-id')
        except Transaction.DoesNotExist:
            transactions = None
        try:
            payments = Invoice.objects.prefetch_related('receiver', 'sender', 'transaction').order_by('-id').all()
        except Invoice.DoesNotExist:
            payments = None
        group_name = 'customer'  # Assuming the group name is 'customer'
        group = Group.objects.get(name=group_name)
        stats = {
            'c': {
                'title': 'Total Customers',
                'value': group.user_set.count(),
            },
            'b': {
                'title': 'Staff Member Count',
                'value': CustomUser.objects.filter(is_staff=True, is_superuser=False).count()
            },
            'a': {
                'title': 'Super admin count',
                'value': CustomUser.objects.filter(is_superuser=True).count()
            },
        }

    context = {
        "page_title": "Dashboard",
        'profile': profile,
        "payees": payees,
        "transactions": transactions,
        'payments': payments,
        'wallet': wallet,
        'invoice_status': INVOICE_STATUS_OPTIONS,
        'invoice_transaction_status': INVOICE_TRANSACTION_STATUS_OPTIONS,
        'stats': stats,
    }
    return render(request, 'payapps/dashboard.html', context)


@login_required
@csrf_protect
@transaction.atomic
def notification_read(request, id):
    notification = Notification.objects.filter(id=id).update(
        is_read='1'
    )
    print()
    return redirect('payapp:payment-action-requested')

# Profile

@login_required
@csrf_protect
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
@csrf_protect
def users_list(request):
    wallets_data = None
    usersArray = []
    users = CustomUser.objects.prefetch_related('wallet_user').all().order_by('-id')
    for user in users:
        try:
            wallet = Wallet.objects.get(user=user)
            user.currency = wallet.currency.iso_code
            user.balance = wallet.amount
        except Wallet.DoesNotExist:
            user.balance = None
        usersArray.append(users)

    context = {
        "page_title": "Users",
        'page_main_heading': "Users List",
        "page_main_description": "Manage users of your application",
        "show_add_new_btn": True,
        'users': users,
    }
    return render(request, 'payapps/admin/users/index.html', context)


@login_required
@transaction.atomic
def users_show(request):
    user = CustomUser.objects.filter(id=request.user)
    return render(request, "payapps/admin/users/show.html", {'selected_user': user})


@login_required
@transaction.atomic
@csrf_protect
@admin_only
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
            return redirect('payapp:users-list')
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
@admin_only
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


@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='auth:login')
@transaction.atomic
@csrf_protect
def users_destroy(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('payapp:users-list')  # Redirect to user list page after deletion


@login_required
@transaction.atomic
@csrf_protect
def users_transaction_history(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    transaction = Transaction.objects.filter(sender=user).prefetch_related(
        'receiver', 'sender').order_by('-id').values()

    context = {
        "page_title": "Transaction History",
        "page_main_heading": "Wallet Transaction History",
        "page_main_description": "Easily add view, your wallet transaction history",
        'transactions': transaction,
        'status': INVOICE_TRANSACTION_STATUS_OPTIONS
    }
    return render(request, 'payapps/payment/transaction-history.html', context)


# Transaction
@login_required
@transaction.atomic
@csrf_protect
def transaction_history(request):
    if request.user.is_superuser:
        transaction = Transaction.objects.all().prefetch_related(
            'receiver', 'sender').order_by('-id')
    elif request.user.is_staff:
        transaction = Transaction.objects.all().prefetch_related(
            'receiver', 'sender').order_by('-id')
    else:
        transaction = Transaction.objects.prefetch_related(
            'receiver', 'sender').filter(sender=request.user).order_by('-id')

    context = {
        "page_title": "Transaction History",
        "page_main_heading": "Wallet Transaction History",
        "page_main_description": "Easily add view, your wallet transaction history",
        'transactions': transaction,
        'status': INVOICE_TRANSACTION_STATUS_OPTIONS
    }
    return render(request, 'payapps/payment/transaction-history.html', context)


@login_required
@transaction.atomic
@csrf_protect
def request_logs(request):
    if request.user.is_superuser:
        transaction = RequestResponseLogs.objects.all().order_by('-id').values()
    else:
        transaction = None

    context = {
        "page_title": "Request Response Logs",
        "page_main_heading": "Transaction Request Response Logs History",
        "page_main_description": "Easily add view, your request transaction logs history",
        'transactions': transaction
    }
    return render(request, 'payapps/payment/request-response-logs.html', context)


# Topup


@login_required
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
@csrf_protect
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
@csrf_protect
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
                    'status': 1,
                    'action': ACTIONS_OPTIONS[1]
                }

                log_transaction(transaction_log)
            except Exception as e:
                print(f"log_transaction Error: {e}")
            print('final wallet')
            print(wallet.amount)
            return redirect('payapp:dashboard')
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
@csrf_protect
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
@csrf_protect
def payment_requests(request):
    sender_requests = Invoice.objects.filter(sender_id=request.user.id).prefetch_related('sender', 'receiver',
                                                                                         'transaction').all()
    receiver_requests = Invoice.objects.filter(receiver_id=request.user.id).prefetch_related('receiver', 'sender'
                                                                                                         'transaction').all()

    # Merge the query sets
    requests = sender_requests.union(receiver_requests)
    context = {
        "page_title": "Payment requests",
        "page_main_heading": "Requested Payments",
        "page_main_description": "Seamless Requests, Swift Payments: Discover Payments Requested",
        'requests': requests
    }
    return render(request, 'payapps/payment/payments-requested.html', context)


@login_required
@transaction.atomic
@csrf_protect
def action_payment_requests(request, action, transaction_id):
    try:
        invoice = Invoice.objects.get(id=transaction_id)
    except Invoice.DoesNotExist:
        return redirect('payapp:payment-action-requested')
    print('bjbkjbkj', invoice.status)

    transaction = invoice.transaction

    sender = transaction.sender
    receiver = transaction.receiver

    if action != 'accept':
        invoice.status = '4'
        invoice.save()

        transaction.status = '2'
        transaction.completed_at = get_timestamp(),
        transaction = transaction.save()

        notification = Notification.objects.create()
        notification.is_read = '1'
        notification.receiver = receiver
        notification.sender = sender
        notification.invoice = invoice
        notification.comment = f'{receiver.username} has rejected your payment request of {transaction.sent_currency.iso_code} {transaction.amount_sent}'
        notification.save()
        print('updated transaction')
        print(transaction)
        request.session['form_errors'] = 'Payment request has been rejected'
    else:
        invoice.status = '2'
        invoice.save()
        print('invoice--')
        print(invoice)
        print(invoice.transaction)
        print('invoice transaction--')
        print(transaction)

        print('sender--', sender)
        print('receiver--', receiver)
        sender_wallet = Wallet.objects.get(user=sender)
        receiver_wallet = Wallet.objects.get(user=receiver)

        print('sender wallet: ')
        print(sender_wallet)
        print('receiver wallet: ', receiver_wallet)

        # Check user base currency and convert the amount as per currency in which user want to transact the amount
        # and then sender's wallet
        transaction_currency = transaction.requested_currency
        try:
            receiver_curr = transaction.receiver_curr
            amount = transaction.amount_requested
            print('transaction_currency')
            print(transaction_currency, transaction_currency.iso_code)
            print('receiver_curr')
            print(receiver_curr, receiver_curr.iso_code)
            amount_to_send = None
            if transaction_currency.iso_code != receiver_curr.iso_code:
                amt_to_transfer = get_exchange_rate(request, receiver_curr.iso_code, amount,
                                                    transaction_currency.iso_code, sender.id)
                print('amt_to_transfer')
                print(amt_to_transfer)
                amount_to_send = amt_to_transfer.get("converted_amt")
            else:
                # If transaction currency and reciever's wallet currency is same then no need to convert
                # amount
                amount_to_send = amount
        except Exception as e:
            print(f"Error: {e}")
        print('amount_to_send')
        print(amount_to_send)
        if receiver_wallet.amount < amount_to_send:
            errors = 'You don\'t have enough amount in your wallet to transfer.'
            # Store errors in session
            request.session['errors'] = errors
            return redirect('payapp:request-payment')

        # Deduct from sender wallet
        updated_sender_wallet_amt = Decimal(sender_wallet.amount)-Decimal(amount_to_send)
        print('updated_sender_wallet_amt')
        print(updated_sender_wallet_amt)
        updated_withdrawal_limit_per = percentage(10, updated_sender_wallet_amt)
        updated_withdrawal_limit = updated_sender_wallet_amt * updated_withdrawal_limit_per

        Wallet.objects.filter(user_id=sender.id).update(
            amount=format(updated_sender_wallet_amt),
            withdrawal_limit=format(updated_sender_wallet_amt - updated_withdrawal_limit)
        )

        print('updated sender wallet')
        print(sender_wallet.amount)
        # Add in receiver wallet
        updated_receiver_wallet_amt = Decimal(receiver_wallet.amount)+Decimal(amount_to_send)
        updated_withdrawal_limit_per = percentage(10, updated_receiver_wallet_amt)
        updated_withdrawal_limit = updated_receiver_wallet_amt * updated_withdrawal_limit_per
        Wallet.objects.filter(user_id=receiver.id).update(
            amount=format(updated_receiver_wallet_amt),
            withdrawal_limit=format(updated_receiver_wallet_amt - updated_withdrawal_limit)
        )
        print('bjsdbkfjbndskjfbkjdsnfkj')
        print('updated receiver wallet')
        print(receiver_wallet.amount)
        # Create Transaction and notification
        print(updated_sender_wallet_amt, updated_receiver_wallet_amt, amount_to_send)
        print(type(updated_sender_wallet_amt), type(updated_receiver_wallet_amt), type(amount_to_send))
        # Update transaction log
        Transaction.objects.filter(id=invoice.transaction_id).update(
            status='1',
            sender_cur_bal=Decimal(updated_sender_wallet_amt),
            receiver_cur_bal=Decimal(updated_receiver_wallet_amt),
            amount_sent=Decimal(amount_to_send),
            sent_currency_id=transaction_currency.id,
            completed_at=get_timestamp()
        )
        print('updated transaction')

        invoice.status = 3
        invoice.save()

        notification = Notification.objects.create()
        notification.is_read = '1'
        notification.receiver = sender
        notification.sender = receiver
        notification.invoice = invoice
        notification.comment = f"{receiver.username} has paid you {transaction_currency.iso_code} {amount_to_send}"
        notification.save()
    return redirect('payapp:payment-action-requested')


@login_required
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
# @transaction.atomic
@csrf_protect
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
                receiver_wallet = Wallet.objects.get(user_id=receiver.id)
                receiver_wallet_amt = receiver_wallet.amount

                invoice_no = random_with_n_digits(15)
                transfer_wallet_amt = None

                if sender.id == receiver.id:
                    errors = 'Can\'t add self to as a payee.'
                    # Store errors in session
                    request.session['errors'] = errors
                    return redirect('payapp:request-payment')
                elif receiver is None:
                    errors = 'The entered payee details doesn\'t exist in our system. Ask your friend '
                    'to join PayGenius to transfer him payment.'
                    # Store errors in session
                    request.session['errors'] = errors
                    return redirect('payapp:request-payment')
                else:
                    # Add payee if not already added
                    # Query the database to find the payee based on sender and receiver
                    try:
                        payee = Payee.objects.get(sender=sender, payee=receiver)
                    except Payee.DoesNotExist:
                        # If payee does not exist, create a new payee
                        payee = Payee.objects.create(sender=sender, payee=receiver)

                    print('payee')
                    print(payee)

                    comment = f"{sender.username} requested payment of amount {transaction_currency.iso_code}{amount} from {receiver.username}"
                    # Create a unpaid transaction log with just sender details
                    # and extend it further on after transacting amt and update the transaction amt after deducting it from wallet
                    transaction_log = {
                        'sender_id': sender.id,
                        "sender_curr_id": sender_currency.id,
                        'sender_prev_bal': sender_wallet_amt,
                        'sender_cur_bal': sender_wallet_amt,
                        'receiver': receiver,
                        'receiver_id': receiver.id,
                        'receiver_curr_id': receiver_currency.id,
                        'receiver_prev_bal': receiver_wallet_amt,
                        'receiver_cur_bal': receiver_wallet_amt,
                        'amount_requested': amount,
                        'comment': comment,
                        'amount_sent': 0,
                        'status': 0,
                        'requested_currency_id': transaction_currency.id,
                        'sent_currency_id': None,
                        'action': ACTIONS_OPTIONS[0]
                    }
                    print('transaction_log')
                    print(transaction_log)
                    transaction = log_transaction(transaction_log)
                    print('transaction')
                    print(transaction)
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
                    notification.is_read = '0'
                    notification.receiver = receiver
                    notification.sender = sender
                    notification.invoice = invoice
                    notification.comment = f"{sender.username} requested payment of amount {transaction_currency.iso_code}{amount}"
                    notification.save()
                    # Clear any existing error messages
                    messages.error(request, None)
                    messages.success(request, 'Payment request has been made to ' + receiver.username)
        except Exception as e:
            print(f"Transaction Error: {e}")
        return redirect('payapp:payment-action-requested')
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
@csrf_protect
@allowed_users(allowed_roles=['customer'])
def request_payment_from_payee(request, request_id):
    receiver = CustomUser.objects.get(pk=request_id)

    print('request_payment_from_payee')
    print(request_id)
    print('receiver')
    print(receiver)

    if request.method == "POST":
        print(45545646545)
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
                                # Check user base currency and convert the amount as per currency in which user want
                                # to transact the amount and then sender's wallet
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
                                'status': 1,
                                'requested_currency_id': transaction_currency.id,
                                'sent_currency_id': sender.id,
                                'action': ACTIONS_OPTIONS[0]
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
                                notification = Notification.objects.get_or_create(invoice_id=invoice.id)
                                notification.is_read = '0'
                                notification.receiver = receiver
                                notification.sender = sender
                                notification.invoice = invoice
                                notification.save()
                                print('notification')
                                print('11665465')
                            except Exception as e:
                                print(f"notification Error: {e}")

                            messages.success(request, 'Payment request has been made to ' + receiver.username)
            except Exception as e:
                print(f"request-payment: {e}")
            return redirect('payapp:payment-action-requested')
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
            return redirect('payapp:my-payee-list')
        elif receiver.is_staff == True:
            request.session['form_errors'] = form.errors
            # Clear any existing error messages
            messages.error(request, None)
            messages.error(request, 'The entered payee details belongs to a restricted user.')
            return redirect('payapp:my-payee-list')
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
@csrf_protect
@transaction.atomic
@allowed_users(allowed_roles=['customer'])
def delete_payee(request, request_id):
    print('request_id')
    print(request_id)
    receiver = CustomUser.objects.get(id=request_id)
    payee = Payee.objects.filter(sender=request.user, payee=receiver)
    payee.delete()
    return redirect('payapp:my-payee-list')


# Transaction
@login_required
@transaction.atomic
@csrf_protect
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
@csrf_protect
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
