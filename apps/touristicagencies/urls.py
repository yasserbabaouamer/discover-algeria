from django.urls import path

from apps.touristicagencies.views import GetTopTours, GetCityTours

APP_URL = 'agencies/'

urlpatterns = [
    path(APP_URL + 'top-tours/', GetTopTours.as_view()),
    path('cities/<int:city_id>/tours', GetCityTours.as_view())
]
