from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="assigned_currency"
    )
    phone = models.CharField(max_length=12, blank=True, null=True)
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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="wallet_user",
    )
    wallet_number = models.CharField(max_length=14, default=0)
    withdrawal_limit = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=11, decimal_places=2,null=True)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="wallet_currency",
        unique=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Payee(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True,
        related_name="payee_sender_id",
        unique=False
    )
    payee = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name="payee_id",
                                 unique=False)
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
    transaction = models.CharField(max_length=50)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True,
        related_name="sender_id",
        unique=False
    )
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                    related_name="receiver_id",
                                    unique=False)
    status = models.CharField(max_length=1, default="0", choices=STATUS_OPTIONS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def __str__(self):
        return str(self.user)


class Transaction(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True,
        null=True,
        related_name="transaction_sender_id"
    )
    sender_curr = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="assigned_sender_currency",
    )
    sender_prev_bal = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    sender_cur_bal = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name="transaction_receiver_id")
    receiver_curr = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="assigned_receiver_currencies",
        unique=False
    )
    receiver_prev_bal = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    receiver_cur_bal = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    amount_requested = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    amount_sent = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    comment = models.CharField(max_length=1000, null=True)
    status = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def __str__(self):
        return str(self.user)


class RequestResponseLogs(models.Model):
    url = models.TextField(null=True)
    user = models.BigIntegerField(null=True)
    request = models.TextField(null=True)
    response = models.TextField(null=True)
    response_code = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def __str__(self):
        return str(self.user)
