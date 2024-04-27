from django.urls import path, include, re_path
from .views import (
    ConversionApiView,
)

app_name = 'conversion'
# URLConfig
urlpatterns = [
    path('<str:currency1>/<str:currency2>/<str:amount_of_currency>', ConversionApiView.as_view(), name="conversion"),

    # re_path('<str:currency1>/<str:currency2>/(?P<amount_of_currency1>\d+)/$', ConversionApiView.as_view(),
    #         name="conversion_3"),
]