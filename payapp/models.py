from django.db import models


# Create your models here.
class User(models.Model):
    STATUS_OPTIONS = [
        ('1', 'Active'),
        ('0', 'In Active'),
    ]
    username = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=50)
    currency_id = models.IntegerField()
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=1, default='0', choices=STATUS_OPTIONS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Wallet(models.Model):
    user_id = models.BigIntegerField()
    amount = models.DecimalField(default=0,decimal_places=2, max_digits=11)
    currency_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Role(models.Model):
    name = models.CharField(max_length=255)
    guard = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Permission(models.Model):
    name = models.CharField(max_length=255)
    group = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class RoleHasPermission(models.Model):
    role_id = models.IntegerField()
    permission_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Payee(models.Model):
    sender_id = models.IntegerField()
    payee_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Invoice(models.Model):
    STATUS_OPTIONS = [
        ('1', 'Active'),
        ('0', 'In Active'),
    ]
    TRANSACTION_STATUS_OPTIONS = [
        ('1', 'Paid'),
        ('0', 'Not paid'),
    ]
    invoice_no = models.CharField(max_length=255, unique=True)
    invoice_date = models.DateField()
    transaction_date = models.DateField()
    transaction_status = models.CharField(max_length=1, default='0', choices=TRANSACTION_STATUS_OPTIONS)
    transaction_id = models.CharField(max_length=50)
    sender_id = models.BigIntegerField()
    receiver_id = models.BigIntegerField()
    status = models.CharField(max_length=1, default='0', choices=STATUS_OPTIONS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    sender_id = models.IntegerField()
    sender_curr_id = models.IntegerField()
    sender_prev_bal = models.DecimalField(max_digits=11, decimal_places=2)
    sender_cur_bal = models.DecimalField(max_digits=11, decimal_places=2)
    receiver_id = models.IntegerField()
    receiver_curr_id = models.IntegerField()
    receiver_prev_bal = models.DecimalField(max_digits=11, decimal_places=2)
    receiver_cur_bal = models.DecimalField(max_digits=11, decimal_places=2)
    amount_requested = models.DecimalField(max_digits=11, decimal_places=2)
    amount_sent = models.DecimalField(max_digits=11, decimal_places=2)
    comment = models.CharField(max_length=1000, null=True)
    status = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class Currency(models.Model):
    name = models.IntegerField()
    iso_code = models.CharField(max_length=5)
    code = models.CharField(max_length=5)
    curr_rate = models.DecimalField(max_digits=11, decimal_places=2)
