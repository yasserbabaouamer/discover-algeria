from django.urls import path

from apps.hotels.views import *

APP_URL = 'hotels/'

urlpatterns = [
    path(APP_URL + 'most-visited/', GetMostVisitedHotelsView.as_view()),
    path(APP_URL + '<int:hotel_id>/', HotelView.as_view()),
    path(APP_URL + '<int:hotel_id>/reviews/', HotelReviewsView.as_view()),
    path(APP_URL + '<int:hotel_id>/rooms/', GetHotelRoomTypes.as_view()),
    path(APP_URL + 'reserve/', RoomReservationView.as_view()),
    path(APP_URL + 'fill/', FillDb.as_view())
]
