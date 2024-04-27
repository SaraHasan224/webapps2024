from django import forms
from .models import User, Currency, Wallet


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
        # fields = "__all__"

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
