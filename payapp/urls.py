from django.urls import path
from . import views
from . import payapp_views

# URLConfig
app_name = 'payapp'

urlpatterns = [
    # path('', views.index),
    # Dashboard Start
    path('', payapp_views.index, name="index"),

    path('dashboard/', payapp_views.dashboard, name="dashboard"),
    # Admin Management
    path('users/list/', payapp_views.users_list, name="users-list"),
    path('users/add-new', payapp_views.users_add, name="users-add-new"),
    path('users/edit/<str:id>', payapp_views.users_edit, name="users-edit"),

    path('roles/list/', payapp_views.roles_list, name="roles-list"),
    path('roles/add-new', payapp_views.roles_add, name="roles-add-new"),
    path('roles/edit/<str:id>', payapp_views.roles_edit, name="roles-edit"),

    path('permission/list/', payapp_views.permission_list, name="permission-list"),
    path('permission/add-new', payapp_views.permission_add, name="permission-add-new"),
    path('permission/edit/<str:id>', payapp_views.permissions_edit, name="permission-edit"),

    path('transaction-history/', payapp_views.transaction_history, name="transaction-history"),
    path('my-wallet/', payapp_views.my_wallet, name="my-wallet"),
    path('my-payees/', payapp_views.my_payees, name="my-payees"),
    path('top-up/', payapp_views.topup, name="topup-wallet"),
    path('create-invoices/', payapp_views.create_invoices, name="create-invoices"),
    # Dashboard END

    path('app-profile/', payapp_views.app_profile, name="app-profile"),
]
