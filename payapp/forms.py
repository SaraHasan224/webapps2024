from datetime import timezone

from django import forms
from django.contrib.auth.models import User, Permission
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.http import request

from payapp.models import Currency, Wallet, Invoice, Payee, CustomUser


class UserForm(forms.ModelForm):
    STATUS_OPTIONS = [
        ('1', 'Active'),
        ('0', 'In Active'),
    ]
    ROLE_OPTIONS = [
        ('1', 'Super Admin'),
        ('2', 'Staff'),
        ('3', 'Customer'),
    ]
    CURRENCY_OPTIONS = [
        ('USD', 'USD - US Dollars'),
        ('GBP', 'GBP - British pounds sterling'),
        ('EUR', 'EUR - Euro'),
    ]
    first_name = forms.CharField(required=True, label='First name ', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your  first name '}))
    last_name = forms.CharField(required=True, label='Last name ', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your last name '}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'hello@example.com'}))
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', "autocomplete": "new-password"}),
    )
    status = forms.ChoiceField(
        choices=STATUS_OPTIONS,
        widget=forms.Select(attrs={'class': 'default-select form-control wide mb-3', 'data-override': 'content-type'})
    )
    role = forms.ChoiceField(
        choices=ROLE_OPTIONS,
        widget=forms.Select(attrs={'class': 'default-select form-control wide mb-3', 'data-override': 'content-type'})
    )
    # date_joined = forms.ChoiceField(required=True,
    #                                 widget=forms.DateField(attrs={'class': 'default-select form-control wide mb-3', 'data-override': 'content-type'})
    # )
    # currency = forms.ChoiceField(
    #     choices=CURRENCY_OPTIONS,
    #     widget=forms.Select(attrs={'class': 'default-select form-control wide mb-3', 'data-override': 'content-type'})
    # )
    username = forms.CharField(required=True, label='Username ', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your  user name '}))

    class Meta:
        model = User

        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'role',
            'is_staff',
            'is_superuser',
            'date_joined',
            'is_active',
            'last_login',
            'is_superuser'
        ]


class WalletTopupForm(forms.ModelForm):
    CURRENCIES = (
        (Currency.objects.get(iso_code='USD').id, 'USD - US Dollars'),
        (Currency.objects.get(iso_code='GBP').id, 'GBP - British pounds sterling'),
        (Currency.objects.get(iso_code='EUR').id, 'EUR - Euro'),
        # Add more choices as needed
    )

    requested_currency = forms.ChoiceField(choices=CURRENCIES)
    amount = forms.FloatField()

    class Meta:
        model = Wallet
        # fields = "__all__"

        fields = [
            'requested_currency',
            'amount'
        ]


class RequestPaymentForm(forms.ModelForm):
    CURRENCIES = (
        (Currency.objects.get(iso_code='USD').id, 'USD - US Dollars'),
        (Currency.objects.get(iso_code='GBP').id, 'GBP - British pounds sterling'),
        (Currency.objects.get(iso_code='EUR').id, 'EUR - Euro'),
        # Add more choices as needed
    )

    receiver = forms.EmailField(required=True, label='Payee Email', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your payee email '}))
    currency = forms.ChoiceField(choices=CURRENCIES)
    amount = forms.FloatField()

    class Meta:
        model = Invoice
        fields = [
            'receiver',
            'currency',
            'amount',
        ]


class MyPayeeForm(forms.ModelForm):
    payee = forms.EmailField(required=True, label='Payee Email', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your payee email '}))

    class Meta:
        model = Payee
        fields = [
            'payee',
        ]


class EditUserForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Username', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your username '}))
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your email '}))
    first_name = forms.CharField(required=True, label='First name', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your first name '}))
    last_name = forms.CharField(required=True, label='Last name', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your last name '}))
    # is_staff = forms.BooleanField(label='Is Staff User', required=True,
    #                               widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    # is_superuser = forms.BooleanField(label='Is Super Admin', required=True,
    #                                   widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    # permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), widget=forms.CheckboxSelectMultiple,
    #                                              required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'groups', 'date_joined']

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['is_superuser'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_staff'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'
        self.fields['groups'].widget.attrs['class'] = 'me-sm-2 default-select form-control wide'
        self.fields['date_joined'].widget.attrs['class'] = 'form-control'

        # Add custom classes to labels
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email'
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['is_superuser'].label = 'Is Superuser'
        self.fields['is_staff'].label = 'Is Staff'
        self.fields['is_active'].label = 'Status'
        self.fields['groups'].label = 'Groups'
        self.fields['date_joined'].label = 'Date Joined'