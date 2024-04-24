from django.shortcuts import render

def index(request):
    context={
        "page_title":"EasyTransact"
    }
    return render(request,'payapps/home.html',context)

def dashboard(request):
    context={
        "page_title":"Dashboard"
    }
    return render(request,'payapps/index.html',context)

def transaction_history(request):
    context={
        "page_title":"Transaction History"
    }
    return render(request,'payapps/transaction-history.html',context)

def topup(request):
    context={
        "page_title":"Top up"
    }
    return render(request,'payapps/transaction-history.html',context)

def create_invoices(request):
    context={
        "page_title":"Create Invoices"
    }
    return render(request,'payapps/create-invoices.html',context)

def app_profile(request):
    context={
        "page_title":"App Profile"
    }
    return render(request,'payapps/apps/app-profile.html',context)


def ui_accordion(request):
    context={
        "page_title":"Accordion"
    }
    return render(request,'payapps/bootstrap/ui-accordion.html',context)


def ui_alert(request):
    context={
        "page_title":"Alert"
    }
    return render(request,'payapps/bootstrap/ui-alert.html',context)


def ui_badge(request):
    context={
        "page_title":"Badge"
    }
    return render(request,'payapps/bootstrap/ui-badge.html',context)


def ui_button(request):
    context={
        "page_title":"Button"
    }
    return render(request,'payapps/bootstrap/ui-button.html',context)


def ui_modal(request):
    context={
        "page_title":"Modal"
    }
    return render(request,'payapps/bootstrap/ui-modal.html',context)


def ui_button_group(request):
    context={
        "page_title":"Button Group"
    }
    return render(request,'payapps/bootstrap/ui-button-group.html',context)


def ui_list_group(request):
    context={
        "page_title":"List Group"
    }
    return render(request,'payapps/bootstrap/ui-list-group.html',context)


def ui_card(request):
    context={
        "page_title":"Card"
    }
    return render(request,'payapps/bootstrap/ui-card.html',context)

def ui_tab(request):
    context={
        "page_title":"Tab"
    }
    return render(request,'payapps/bootstrap/ui-tab.html',context)

def form_element(request):
    context={
        "page_title":"Form Element"
    }
    return render(request,'payapps/forms/form-element.html',context)


def form_pickers(request):
    context={
        "page_title":"Pickers"
    }
    return render(request,'payapps/forms/form-pickers.html',context)


def form_validation(request):
    context={
        "page_title":"Form Validation"
    }
    return render(request,'payapps/forms/form-validation.html',context)
