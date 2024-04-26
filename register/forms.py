from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    CURRENCIES = (
        ('USD', 'USD - US Dollars'),
        ('GBP', 'GBP - British pounds sterling'),
        ('EUR', 'EUR - Euro'),
        # Add more choices as needed
    )

    currency = forms.ChoiceField(choices=CURRENCIES)
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'hello@example.com'}))
    username = forms.CharField(required=True, label='Username ', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your  user name '}))
    first_name = forms.CharField(required=True, label='First name ', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your  first name '}))
    last_name = forms.CharField(required=True, label='Last name ', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your last name '}))

    # def save(self, commit=True):
    #     user = super(UserCreationForm, self).save(commit=False)
    #     user.currency = self.cleaned_data["currency"]
    #     if commit:
    #         user.save()
    #     return user

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'currency']


class EditProfile(UserChangeForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'hello@example.com'}))
