from django.urls import path
from . import payapp_views

# URLConfig
app_name = 'payapp'

urlpatterns = [
    # path('', views.index),
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
    path('my-payees/', payapp_views.my_payees, name="my-payees"),
    path('top-up/', payapp_views.topup, name="topup-wallet"),
    path('request-payment/', payapp_views.request_payment, name="request-payment"),
    # Dashboard END

    path('app-profile/', payapp_views.app_profile, name="app-profile"),
]
