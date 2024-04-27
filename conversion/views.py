import json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import JsonResponse
from rest_framework import permissions
from .serializers import CurrencySerializer
from payapp.models import Currency
from decimal import Decimal
from django.forms.models import model_to_dict
import requests


# @APIView()
# def get(request, currency1, currency2, amount_of_currency):
#     try:
#         currency = Currency.objects.get(pk=currency1)
#         serializer = CurrencySerializer(currency)
#         return Response(serializer.data)
#     except Currency.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
# #     OR
#         currency = get_object_or_404(Currency, pk=name)

class ConversionApiView(APIView):
    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        try:
            amount = format(kwargs.get('amount_of_currency'))
            from_currency_code = kwargs.get('currency1')
            to_currency_code = kwargs.get('currency2')

            from_currency = get_object_or_404(Currency, code=from_currency_code)
            to_currency = get_object_or_404(Currency, code=to_currency_code)

            if from_currency.curr_rate == 0:
                err = {"error": "Conversion rate for the source currency is zero"}
                return Response(err, status=status.HTTP_400_BAD_REQUEST)

            exchange_rate = get_exchange_rate(from_currency_code, to_currency_code)
            converted_amount = (Decimal(amount) / from_currency.curr_rate) * to_currency.curr_rate
            result = {
                # 'from_curr_amt': amount,
                # 'from_rate': from_currency.curr_rate,
                # 'to_rate': to_currency.curr_rate,
                # "converted_amount": float(converted_amount),
                'from_curr': from_currency_code,
                'to_curr': to_currency_code,
                'exchange_rate': exchange_rate,
                'converted_amt': float(amount) * exchange_rate
            }
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Currency.DoesNotExist:
            err = {"error": "One of the currency codes does not exist in the database"}
            return Response(err, status=status.HTTP_400_BAD_REQUEST)


def get_exchange_rate(base_currency, target_currency):
    try:
        response = requests.get(f"https://v6.exchangerate-api.com/v6/526fc43143fe0f5c6dab293f/latest/"+base_currency)
        data = response.json()
        if response.status_code == 200:
            if target_currency in data['conversion_rates']:
                return data['conversion_rates'][target_currency]
            else:
                return f"Target currency '{target_currency}' not found."
        else:
            return "Failed to retrieve exchange rates."
    except Exception as e:
        return f"Error: {e}"
