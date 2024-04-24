from django.urls import path
from . import views

app_name = 'auth'
# URLConfig
urlpatterns = [
    path('login/',views.page_login,name="login"),
    path('register/',views.page_register,name="register"),
    path('forgot-password/',views.page_forgot_password,name="forgot-password"),
]