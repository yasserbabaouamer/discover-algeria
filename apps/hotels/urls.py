from django.urls import path

from apps.hotels.views import *

APP_URL = 'hotels/'

urlpatterns = [
    path(APP_URL + 'most-visited/', GetMostVisitedHotelsView.as_view()),
    path(APP_URL + '<int:hotel_id>/', HotelAPIView.as_view()),
    path(APP_URL + 'reviews/<int:hotel_id>/', HotelReviewsAPIView.as_view()),
    path(APP_URL + 'fill/', FillDb.as_view())
]
