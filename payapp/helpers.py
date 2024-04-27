import requests
from random import randint

from payapp.models import RequestResponseLogs, Wallet, Currency


def random_with_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def percentage(part, whole):
    return 100 * part / whole
    # return 100 * float(part) / float(whole)


def get_exchange_rate(base_currency_code, base_rate, target_currency_code, userId):
    try:
        print('base_currency')
        print(base_currency_code)
        print('target_currency_code')
        print(target_currency_code)
        print('base_rate')
        print(base_rate)
        base_url = "http://127.0.0.1:8000/"
        url = base_url+f"conversion/{base_currency_code}/{target_currency_code}/{base_rate}"
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


def assign_wallet_on_registration(user, profile):
    try:
        base_currency_charge = 1000.00
        base_currency = 'GBP'
        user_currency = profile.currency.iso_code

        user_id = profile.user_id
        if user_currency != base_currency:
            conversion = get_exchange_rate(base_currency, base_currency_charge, user_currency, user_id)
            print(conversion)
            wallet_amt = conversion.get("converted_amt")
        else:
            wallet_amt = base_currency_charge

        withdrawal_limit = percentage(10, wallet_amt)
        currency = Currency.objects.get(iso_code=user_currency)

        wallet = Wallet.objects.create()
        wallet.user_id = user.id
        wallet.wallet_number = random_with_n_digits(14)
        wallet.withdrawal_limit = wallet_amt-withdrawal_limit
        wallet.amount = wallet_amt
        wallet.currency_id = currency.id
        wallet.save()
        return wallet
    except Exception as e:
        return f"Error: {e}"
