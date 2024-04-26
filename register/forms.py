from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User

from payapp.models import Profile, Currency


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

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.save()
    #
    #     try:
    #         currency = Currency.objects.get(iso_code=self.cleaned_data['currency'])
    #     except Currency.DoesNotExist:
    #         raise ValueError("One of the currency codes does not exist in the database")
    #     if currency.curr_rate == 0:
    #         raise ValueError("Conversion rate for the source currency is zero")
    #
    #     # profile = Profile.objects.create(user=user, currency=currency.id)
    #     return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']


class EditProfile(UserChangeForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'hello@example.com'}))
