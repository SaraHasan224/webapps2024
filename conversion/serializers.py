from rest_framework import serializers
from payapp.models import Currency


class CurrencySerializer(serializers.Serializer):
    name = serializers.IntegerField()
    iso_code = serializers.CharField(max_length=5)
    code = serializers.CharField(max_length=5)
    curr_rate = serializers.DecimalField(max_digits=11, decimal_places=2)


def convert_currency(amount, from_currency_code, to_currency_code):
    try:
        from_currency = Currency.objects.get(iso_code=from_currency_code)
        to_currency = Currency.objects.get(iso_code=to_currency_code)
    except Currency.DoesNotExist:
        raise ValueError("One of the currency codes does not exist in the database")

# class CurrencySerializer(serializers.Serializer):
#     name = serializers.IntegerField()
#     iso_code = serializers.CharField(max_length=5)
#     code = serializers.CharField(max_length=5)
#     curr_rate = serializers.DecimalField(max_digits=11, decimal_places=2)
#
#
# def convert_currency(amount, from_currency_code, to_currency_code):
#     try:
#         from_currency = Currency.objects.get(iso_code=from_currency_code)
#         to_currency = Currency.objects.get(iso_code=to_currency_code)
#     except Currency.DoesNotExist:
#         raise ValueError("One of the currency codes does not exist in the database")
#
#     if from_currency.curr_rate == 0:
#         raise ValueError("Conversion rate for the source currency is zero")
#
#     converted_amount = (amount / from_currency.curr_rate) * to_currency.curr_rate
#     return converted_amount
