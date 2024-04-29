import requests
from random import randint

from payapp.models import RequestResponseLogs, Wallet, Currency, Transaction, CustomUser, Invoice


def random_with_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def percentage(part, whole):
    return 100 * part / whole
    # return 100 * float(part) / float(whole)


def get_exchange_rate(request, base_currency_code, base_rate, target_currency_code, userId):
    try:
        print('--get_exchange_rate--')
        print(base_currency_code)
        print(target_currency_code)
        print(base_rate)
        base_url = "http://127.0.0.1:8000/"
        url = base_url + f"conversion/{base_currency_code}/{target_currency_code}/{base_rate}"
        print("url")
        print(url)
        response = requests.get(url)
        data = response.json()
        print('data')
        print(data)
        # Create a new instance of MyModel
        request_lgs = RequestResponseLogs()

        # Set attributes of the instance
        request_lgs.url = url
        request_lgs.user_id = userId
        request_lgs.response = data
        request_lgs.response_code = response.status_code
        # Set other fields as needed
        # Save the instance to the database
        request_lgs.save()
        print('result')
        print(data)
        if response.status_code == 200:
            return data
        else:
            return "Failed to retrieve exchange rates."
    except Exception as e:
        return f"Error: {e}"


def assign_wallet_on_registration(request, user, profile):
    try:
        base_currency_charge = 1000.00
        base_currency = 'GBP'
        user_currency = profile.currency.iso_code

        user_id = profile.user_id

        print('user_id')
        print(user_id)
        print('base_currency')
        print(base_currency)
        print('user_currency')
        print(user_currency)
        if user_currency != base_currency:
            print('Ready for conversion? ')
            print(base_currency, base_currency_charge, user_currency, user_id)
            conversion = get_exchange_rate(request, base_currency, base_currency_charge, user_currency, user_id)
            print('conversion')
            print(conversion)
            wallet_amt = conversion.get("converted_amt")
        else:
            wallet_amt = base_currency_charge

        print('wallet_amt')
        print(wallet_amt)
        withdrawal_limit = percentage(10, wallet_amt)
        currency = Currency.objects.get(iso_code=user_currency)

        wallet = Wallet.objects.create()
        wallet.user_id = user.id
        wallet.wallet_number = random_with_n_digits(14)
        wallet.withdrawal_limit = wallet_amt - withdrawal_limit
        wallet.amount = wallet_amt
        wallet.currency_id = currency.id
        wallet.save()
        print('wallet setup ')
        print(wallet)
        return wallet
    except Exception as e:
        return f"assign_wallet_on_registration Error: {e}"

def create_invoice(invoice_data):
    try:
        transaction = invoice_data.get('transaction')
        invoice = Invoice.objects.create()
        invoice.invoice_no = invoice_data.get('invoice_no')
        invoice.invoice_date = invoice_data.get('invoice_date')
        invoice.transaction_date = invoice_data.get('transaction_date')
        invoice.transaction_status = invoice_data.get('transaction_status')
        invoice.transaction = transaction
        invoice.sender = invoice_data.get('sender')
        invoice.receiver = invoice_data.get('receiver')
        invoice.status = invoice_data.get('status')
        invoice.save()
        return invoice
    except Exception as e:
        print(f"Transaction Error: {e}")

def update_transaction(transaction_log, transaction_id):
    print("log_transaction")
    print(type(transaction_log))
    print(transaction_log.get('sender_id'))
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        transaction.sender_id = transaction_log.get('sender_id')
        transaction.sender_curr_id = transaction_log.get('sender_curr_id')
        transaction.sender_prev_bal = transaction_log.get('sender_prev_bal')
        transaction.sender_cur_bal = transaction_log.get('sender_cur_bal')
        transaction.receiver_id = transaction_log.get('receiver_id')
        transaction.receiver_curr_id = transaction_log.get('receiver_curr_id')
        transaction.receiver_prev_bal = transaction_log.get('receiver_prev_bal')
        transaction.receiver_cur_bal = transaction_log.get('receiver_cur_bal')
        transaction.amount_requested = transaction_log.get('amount_requested')
        transaction.amount_sent = transaction_log.get('amount_sent')
        transaction.comment = transaction_log.get('comment')
        transaction.status = transaction_log.get('status')
        transaction.save()
        return transaction
    except Exception as e:
        print(f"Transaction Error: {e}")

def log_transaction(transaction_log):
    print("log_transaction")
    print(type(transaction_log))
    print(transaction_log.get('sender_id'))
    try:
        transaction = Transaction.objects.create()
        transaction.sender_id = transaction_log.get('sender_id')
        transaction.sender_curr_id = transaction_log.get('sender_curr_id')
        transaction.sender_prev_bal = transaction_log.get('sender_prev_bal')
        transaction.sender_cur_bal = transaction_log.get('sender_cur_bal')
        transaction.receiver_id = transaction_log.get('receiver_id')
        transaction.receiver_curr_id = transaction_log.get('receiver_curr_id')
        transaction.receiver_prev_bal = transaction_log.get('receiver_prev_bal')
        transaction.receiver_cur_bal = transaction_log.get('receiver_cur_bal')
        transaction.amount_requested = transaction_log.get('amount_requested')
        transaction.amount_sent = transaction_log.get('amount_sent')
        transaction.comment = transaction_log.get('comment')
        transaction.comment = transaction_log.get('comment')
        transaction.requested_currency_id = transaction_log.get('requested_currency_id')
        transaction.sent_currency_id = transaction_log.get('sent_currency_id')
        transaction.save()
        return transaction
    except Exception as e:
        print(f"Transaction Error: {e}")


def transaction_status():
    return [
        ("Transferred", 1),
        ("Pending", 0),
    ]

def find_customer_by_email(user_email):
    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        user = None
    return user

def update_sender_wallet(sender_wallet, transfer_wallet_amt, action):
    if action == 'subtract':
        updated_sender_wallet_amt = float(sender_wallet) - float(transfer_wallet_amt)
    elif action == 'add':
        updated_sender_wallet_amt = float(sender_wallet) + float(transfer_wallet_amt)

    print('updated_sender_wallet_amt')
    print(updated_sender_wallet_amt)
    print('updated_sender_wallet_amt')
    print(updated_sender_wallet_amt)
    sender_withdrawal_limit = percentage(10, updated_sender_wallet_amt)
    print('sender_withdrawal_limit')
    print(sender_withdrawal_limit)
    try:
        sender_wallet.amount = updated_sender_wallet_amt
        sender_wallet.withdrawal_limit = updated_sender_wallet_amt - sender_withdrawal_limit
        sender_wallet.save()
    except Exception as e:
        print(f"Wallet Error: {e}")

    return sender_wallet