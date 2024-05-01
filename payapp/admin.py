from django.contrib import admin

from .models import Wallet, Payee, Invoice, Currency, Transaction, CustomUser

admin.site.register(CustomUser)
admin.site.register(Wallet)
admin.site.register(Payee)
admin.site.register(Invoice)
admin.site.register(Currency)
admin.site.register(Transaction)
