from django.urls import path, include
from . import views

app_name = 'auth'
# URLConfig
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', views.page_register, name="register"),
    path('login/', views.page_login, name="login"),
    path('logout/', views.logout_user, name="logout"),

    # path('change-password/', views.page_register, name="password_change"),
    # path('confirm-change-password/', views.page_register, name="password_change_done"),
    # path('password-reset/', views.page_register, name="password_reset"),
    # path('confirm-reset-password/', views.page_register, name="password_reset_done"),
    # path('reset-password/<uidb64>/<token>/', views.page_register, name="password_reset_confirm"),
    # path('reset-confirm/', views.page_register, name="password_reset_complete"),
    path('forgot-password/', views.page_forgot_password, name="forgot-password"),
]
