from django.shortcuts import render


def index(request):
    context = {
        "page_title": "EasyTransact"
    }
    return render(request, 'payapps/home.html', context)


def dashboard(request):
    context = {
        "page_title": "Dashboard"
    }
    return render(request, 'payapps/index.html', context)


# Profile
def app_profile(request):
    context = {
        "page_title": "App Profile"
    }
    return render(request, 'payapps/apps/app-profile.html', context)

# Admin Management
def users_list(request):
    context = {
        "page_title": "Users",
        'page_main_heading': "Users List",
        "page_main_description": "Manage users of your application",
        "show_add_new_btn": True
    }
    return render(request, 'payapps/users/index.html', context)


def users_add(request):
    context = {
        "page_title": "Users",
        'parent_module': "User",
        'child_module': "Add New",
        'form_title': "Add New User Form"
    }
    return render(request, 'payapps/users/add.html', context)


def users_edit(request, id):
    context = {
        "page_title": "Users",
        'parent_module': "User",
        'child_module': "Edit New",
        'form_title': "Edit User Form",
        'id': id
    }
    return render(request, 'payapps/users/edit.html', context)


def roles_list(request):
    context = {
        "page_title": "Roles",
        'page_main_heading': "Roles List",
        "page_main_description": "Manage roles in your application",
        "show_add_new_btn": True
    }
    return render(request, 'payapps/roles/index.html', context)


def roles_add(request):
    context = {
        "page_title": "Roles",
        'parent_module': "Roles",
        'child_module': "Add New",
        'form_title': "Add New Roles Form"
    }
    return render(request, 'payapps/roles/add.html', context)


def roles_edit(request, id):
    context = {
        "page_title": "Roles",
        'parent_module': "Roles",
        'child_module': "Edit New",
        'form_title': "Edit Roles Form"
    }
    return render(request, 'payapps/roles/edit.html', context)


def permission_list(request):
    context = {
        "page_title": "Permissions",
        'page_main_heading': "Permissions List",
        "page_main_description": "Manage permissions for your application",
        "show_add_new_btn": True
    }
    return render(request, 'payapps/permissions/index.html', context)


def permission_add(request):
    context = {
        "page_title": "Permissions",
        'parent_module': "Permission",
        'child_module': "Add New",
        'form_title': "Add New Permission Form"
    }
    return render(request, 'payapps/permissions/add.html', context)


def permissions_edit(request, id):
    context = {
        "page_title": "Permission",
        'parent_module': "Permission",
        'child_module': "Edit New",
        'form_title': "Edit Permission Form"
    }
    return render(request, 'payapps/roles/edit.html', context)


# Transaction
def transaction_history(request):
    context = {
        "page_title": "Transaction History",
        "page_main_heading": "Wallet Transaction History",
        "page_main_description": "Easily add view, your wallet transaction history"
    }
    return render(request, 'payapps/payment/transaction-history.html', context)


# Topup
def topup(request):
    context = {
        "page_title": "Top up",
        "page_main_heading": "Wallet Top up",
        "page_main_description": "Easily add funds, manage balance, and top up wallet"
    }
    return render(request, 'payapps/payment/wallet-topup.html', context)
def my_payees(request):
    context = {
        "page_title": "My Payees",
        "page_main_heading": "Manage My Payees",
        "page_main_description": "Conveniently view your payees and request payments from them"
    }
    return render(request, 'payapps/payment/payees.html', context)

def my_wallet(request):
    context = {
        "page_title": "My Wallet",
        "page_main_heading": "Wallet Top up",
        "page_main_description": "Conveniently view your wallet"
    }
    return render(request, 'payapps/payment/wallet.html', context)


def create_invoices(request):
    context = {
        "page_title": "Create Invoices"
    }
    return render(request, 'payapps/create-invoices.html', context)
