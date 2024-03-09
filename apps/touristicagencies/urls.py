from django.urls import path

from apps.touristicagencies.views import GetTopTours

APP_URL = 'agencies/'

urlpatterns = [
    path(APP_URL + 'top-tours/', GetTopTours.as_view())
]
