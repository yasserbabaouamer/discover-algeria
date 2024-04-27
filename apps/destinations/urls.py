from django.urls import path

from apps.destinations.views import *

APP_URL = 'destinations/'

urlpatterns = [
    path(APP_URL + 'top/', TopDestinationsView.as_view()),
    path(APP_URL + 'cities/', GetCityDetailsView.as_view()),
    path(APP_URL + 'country-codes/', CountryCodeView.as_view()),
]
