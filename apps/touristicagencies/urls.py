from django.urls import path

from apps.touristicagencies.views import GetTopTours, GetCityTours, GetTourDetails

APP_URL = 'agencies/'

urlpatterns = [
    path(APP_URL + 'top-tours/', GetTopTours.as_view()),
    path(APP_URL + 'tours/<int:tour_id>/', GetTourDetails.as_view()),
    path('cities/<int:city_id>/tours/', GetCityTours.as_view()),
]
