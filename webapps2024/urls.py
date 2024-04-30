"""
URL configuration for webapps2024 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from payapp import payapp_views

handler404 = 'payapp.views.page_error_404'
handler500 = 'payapp.views.page_error_500'
handler503 = 'payapp.views.page_error_503'
handler403 = 'payapp.views.page_error_403'
handler400 = 'payapp.views.page_error_400'

urlpatterns = [
    # Other URL patterns...
    path('admin/', admin.site.urls),
    # path('', include('payapp.urls', namespace='payapp')),
    path('', include('register.urls', namespace='auth')),
    path('conversion/', include('conversion.urls', namespace='conversion')),


    # Dashboard Start
    path('', payapp_views.index, name="index"),

    path('dashboard/', payapp_views.dashboard, name="dashboard"),
    # # Admin Management
    path('users/list/', payapp_views.users_list, name="users-list"),
    path('users/add-new', payapp_views.users_add, name="users-add-new"),
    path('users/edit/<str:id>', payapp_views.users_edit, name="users-edit"),
    path('users/delete/<str:user_id>', payapp_views.users_destroy, name="users-delete"),

    path('transaction-history/', payapp_views.transaction_history, name="transaction-history"),
    path('my-wallet/', payapp_views.my_wallet, name="my-wallet"),

    path('request-payment/', payapp_views.request_payment, name="request-payment"),
    path('payment-requests/', payapp_views.payment_requests, name="payment-requests"),
    path('payment-requests/<str:invoice_no>/', payapp_views.action_payment_requests, name="pay-request-action"),

    path('top-up/', payapp_views.topup, name="topup-wallet"),
    path('top-up-wallet/', payapp_views.topup_wallet_request, name="topup-wallet-amt"),

    path('my-payees/', payapp_views.my_payees, name="my-payees"),
    path('my-payees/list/', payapp_views.payees_list, name="my-payee-list"),

    path('request-payee/<str:request_id>', payapp_views.request_payment_from_payee, name="request-payee"),
    path('delete-payee/<str:request_id>', payapp_views.delete_payee, name="delete-payee"),
    # Dashboard END

    path('app-profile/', payapp_views.app_profile, name="app-profile"),
]

