from django.urls import path

from .views import *

APP_URL = 'hotels/'

urlpatterns = [
    path(APP_URL + 'top/', GetTopHotelsView.as_view()),
    path(APP_URL + '<int:hotel_id>/', GetHotelDetailsView.as_view()),
    path(APP_URL + '<int:hotel_id>/reviews/', HotelReviewsView.as_view()),
    path(APP_URL + '<int:hotel_id>/rooms/', GetHotelRoomTypes.as_view()),
    path(APP_URL + 'reserve/', RoomReservationView.as_view()),
    path('cities/<int:city_id>/hotels', SearchHotelsByCity.as_view()),
    path(APP_URL + 'amenities/', HotelAmenities.as_view()),
    path(APP_URL + 'owner/', OwnerHotelsView.as_view()),
]
