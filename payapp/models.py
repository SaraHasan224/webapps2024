from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.db.models.signals import post_save
from django.dispatch import receiver


# class CustomUser(AbstractUser):
#     CURRENCIES_OPTIONS = (
#         ('USD', 'USD - US Dollars'),
#         ('GBP', 'GBP - British pounds sterling'),
#         ('EUR', 'EUR - Euro'),
#     )
#
#     currency = models.CharField(max_length=3, default='0', choices=CURRENCIES_OPTIONS)


class Currency(models.Model):
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=5)
    code = models.CharField(max_length=5)
    curr_rate = models.DecimalField(max_digits=11, decimal_places=2)


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="assigned_profile",
    )
    currency_id = models.IntegerField(null=True)
    # currency_id = models.OneToOneField(Currency, on_delete=models.CASCADE, blank=True)
    phone = models.CharField(default=200, max_length=12, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            profile = Profile.objects.create(user=instance)
            profile.save()

    def __str__(self):
        return self.user.username


class Wallet(models.Model):
    user_id = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=11)
    currency = models.OneToOneField(
        Currency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="wallet_currency",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def __str__(self):
        return str(self.user)


class Payee(models.Model):
    sender_id = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
    payee_id = models.IntegerField()
    # payee_id = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def __str__(self):
        return str(self.user)


class Invoice(models.Model):
    STATUS_OPTIONS = [
        ("1", "Active"),
        ("0", "In Active"),
    ]
    TRANSACTION_STATUS_OPTIONS = [
        ("1", "Paid"),
        ("0", "Not paid"),
    ]
    invoice_no = models.CharField(max_length=255, unique=True)
    invoice_date = models.DateField()
    transaction_date = models.DateField()
    transaction_status = models.CharField(
        max_length=1, default="0", choices=TRANSACTION_STATUS_OPTIONS
    )
    transaction_id = models.CharField(max_length=50)
    sender_id = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
    receiver_id = models.BigIntegerField()
    # receiver_id = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=1, default="0", choices=STATUS_OPTIONS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def __str__(self):
        return str(self.user)


class Transaction(models.Model):
    sender_id = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
    sender_curr_id = models.OneToOneField(
        Currency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="assigned_sender_currency",
    )
    sender_prev_bal = models.DecimalField(max_digits=11, decimal_places=2)
    sender_cur_bal = models.DecimalField(max_digits=11, decimal_places=2)
    receiver_id = models.IntegerField()
    receiver_curr_id = models.OneToOneField(
        Currency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="assigned_receiver_currency",
    )
    # receiver_id = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    receiver_prev_bal = models.DecimalField(max_digits=11, decimal_places=2)
    receiver_cur_bal = models.DecimalField(max_digits=11, decimal_places=2)
    amount_requested = models.DecimalField(max_digits=11, decimal_places=2)
    amount_sent = models.DecimalField(max_digits=11, decimal_places=2)
    comment = models.CharField(max_length=1000, null=True)
    status = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def __str__(self):
        return str(self.user)