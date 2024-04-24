from django.urls import path
from . import views
from . import payapp_views
# URLConfig
app_name = 'payapp'

urlpatterns = [
    # path('', views.index),
    # Dashboard Start
    path('',payapp_views.index,name="index"),
    path('dashboard/',payapp_views.dashboard,name="dashboard"),
    path('index/',payapp_views.index,name="index"),
    path('transaction-history/',payapp_views.transaction_history,name="transaction-history"),
    path('top-up/',payapp_views.topup,name="topup-wallet"),
    path('create-invoices/',payapp_views.create_invoices,name="create-invoices"),
    # Dashboard END

    path('app-profile/',payapp_views.app_profile,name="app-profile"),

    path('ui-accordion/',payapp_views.ui_accordion,name="ui-accordion"),
    path('ui-alert/',payapp_views.ui_alert,name="ui-alert"),
    path('ui-badge/',payapp_views.ui_badge,name="ui-badge"),
    path('ui-button/',payapp_views.ui_button,name="ui-button"),
    path('ui-modal/',payapp_views.ui_modal,name="ui-modal"),
    path('ui-button-group/',payapp_views.ui_button_group,name="ui-button-group"),
    path('ui-list-group/',payapp_views.ui_list_group,name="ui-list-group"),
    path('ui-card/',payapp_views.ui_card,name="ui-card"),
    path('ui-tab/',payapp_views.ui_tab,name="ui-tab"),

    path('form-element/',payapp_views.form_element,name="form-element"),
    path('form-pickers/',payapp_views.form_pickers,name="form-pickers"),
    path('form-validation/',payapp_views.form_validation,name="form-validation"),
]