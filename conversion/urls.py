from django.urls import path, include
from .views import (
    ConversionApiView,
)

app_name = 'conversion'
# URLConfig
urlpatterns = [
    path('<str:currency1>', ConversionApiView.as_view(), name="conversion"),
    path('<str:currency1>/<str:currency2>/<str:amount_of_currency1>', ConversionApiView.as_view(), name="conversion"),
]