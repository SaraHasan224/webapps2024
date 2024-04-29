from datetime import timezone

from django import forms
from django.contrib.auth.models import User, Permission, Group
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.http import request

from payapp.models import Currency, Wallet, Invoice, Payee, CustomUser


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
        attrs={'class': 'form-control', 'placeholder': 'Enter your payee email '}), disabled=True)
    currency = forms.ChoiceField(choices=CURRENCIES)
    amount = forms.FloatField()

    class Meta:
        model = Invoice
        fields = [
            'receiver',
            'currency',
            'amount',
        ]

    def __init__(self, *args, **kwargs):
        super(RequestPaymentForm, self).__init__(*args, **kwargs)

        initial = kwargs.pop('initial', None)
        super(RequestPaymentForm, self).__init__(*args, **kwargs)
        # Check if initial contains email_addr
        if initial is not None:
            if 'email_addr' in initial:
                email_addr = initial.get('email_addr')
            else:
                email_addr = None
            if email_addr is not None:
                self.fields['receiver'].initial = email_addr
        else:
            email_addr = None

class MyPayeeForm(forms.ModelForm):
    payee_email = forms.EmailField(required=True, label='Payee Email', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your payee email '}))

    class Meta:
        model = Payee
        fields = [
            'payee_email',
        ]


class UserForm(forms.ModelForm):
    STATUS_OPTIONS = [
        ('1', 'Active'),
        ('0', 'In Active'),
    ]
    ROLE_OPTIONS = [
        (Group.objects.get(name='superadmin').id, 'Super Admin'),
        (Group.objects.get(name='staff').id, 'Staff'),
        (Group.objects.get(name='customer').id, 'Customer'),
    ]
    CURRENCIES = (
        (Currency.objects.get(iso_code='USD').id, 'USD - US Dollars'),
        (Currency.objects.get(iso_code='GBP').id, 'GBP - British pounds sterling'),
        (Currency.objects.get(iso_code='EUR').id, 'EUR - Euro'),
        # Add more choices as needed
    )

    first_name = forms.CharField(required=True, label='First name ', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your  first name '}))
    last_name = forms.CharField(required=True, label='Last name ', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your last name '}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'hello@example.com'}))
    password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    status = forms.ChoiceField(
        choices=STATUS_OPTIONS,
        widget=forms.Select(attrs={'class': 'default-select form-control wide mb-3', 'data-override': 'content-type'})
    )
    role = forms.ChoiceField(
        choices=ROLE_OPTIONS,
        widget=forms.Select(attrs={'class': 'default-select form-control wide mb-3', 'data-override': 'content-type'})
    )
    currency = forms.ChoiceField(choices=CURRENCIES)
    username = forms.CharField(required=True, label='Username ', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your  user name '}))

    class Meta:
        model = CustomUser

        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
            'role',
            'is_staff',
            'is_superuser',
            'is_active',
            'is_superuser'
        ]


class EditUserForm(forms.ModelForm):
    CURRENCIES = (
        (Currency.objects.get(iso_code='USD').id, 'USD - US Dollars'),
        (Currency.objects.get(iso_code='GBP').id, 'GBP - British pounds sterling'),
        (Currency.objects.get(iso_code='EUR').id, 'EUR - Euro'),
        # Add more choices as needed
    )
    ROLE_OPTIONS = [
        (Group.objects.get(name='superadmin').id, 'Super Admin'),
        (Group.objects.get(name='staff').id, 'Staff'),
        (Group.objects.get(name='customer').id, 'Customer'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_OPTIONS,
        widget=forms.Select(attrs={'class': 'default-select form-control wide mb-3', 'data-override': 'content-type'})
    )
    currency = forms.ChoiceField(
        choices=CURRENCIES,
        widget=forms.Select(attrs={'class': 'default-select form-control wide mb-3', 'data-override': 'content-type'})
    )
    username = forms.CharField(required=True, label='Username', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your username '}))
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your email '}))
    first_name = forms.CharField(required=True, label='First name', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your first name '}))
    last_name = forms.CharField(required=True, label='Last name', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your last name '}))
    date_joined = forms.DateTimeField(label='Date Joined', disabled=True)

    # is_staff = forms.BooleanField(label='Is Staff User', required=True,
    #                               widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    # is_superuser = forms.BooleanField(label='Is Super Admin', required=True,
    #                                   widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    # permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), widget=forms.CheckboxSelectMultiple,
    #                                              required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active',
                  'date_joined']

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['is_superuser'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_staff'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'
        self.fields['role'].widget.attrs['class'] = 'me-sm-2 default-select form-control wide'
        self.fields['date_joined'].widget.attrs['class'] = 'form-control'
        self.fields['currency'].widget.attrs['class'] = 'me-sm-2 default-select form-control wide'

        # Add custom classes to labels
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email'
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['is_superuser'].label = 'Is Superuser'
        self.fields['is_staff'].label = 'Is Staff'
        self.fields['is_active'].label = 'Status'
        self.fields['role'].label = 'Role'
        self.fields['date_joined'].label = 'Date Joined'

        initial = kwargs.pop('initial', None)
        print('initial')
        print(initial)
        super(EditUserForm, self).__init__(*args, **kwargs)
        # Check if initial contains group_id
        if initial is not None:
            if 'group_id' in initial:
                group_id = initial.get('group_id')
            else:
                group_id = None
            if group_id is not None:
                self.fields['role'].initial = group_id
        else:
            group_id = None