from django.urls import path

from apps.destinations.views import *

urlpatterns = [
    path('destinations/top/', TopDestinationsView.as_view()),
    path('cities', GetCityDetailsView.as_view())
]
