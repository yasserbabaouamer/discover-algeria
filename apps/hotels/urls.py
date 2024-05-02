from django.urls import path

from .views import *

APP_URL = 'hotels/'

urlpatterns = [
    path(APP_URL + 'top/', GetTopHotelsView.as_view()),
    path(APP_URL + '<int:hotel_id>/', GetHotelDetailsView.as_view()),
    path(APP_URL + '<int:hotel_id>/reviews/', ListCreateHotelReviewView.as_view()),
    path(APP_URL + '<int:hotel_id>/rooms/', GetHotelRoomTypes.as_view()),
    path(APP_URL + 'reserve/', CreateReservationView.as_view()),
    path('cities/<int:city_id>/hotels', SearchHotelsByCity.as_view()),
    path(APP_URL + 'amenities/', HotelAmenities.as_view()),
    path('owner/' + APP_URL, ListCreateOwnerHotelView.as_view()),
    path('owner/' + APP_URL + '<int:hotel_id>/', ManageOwnerHotelDetailsView.as_view()),
    path('owner/' + APP_URL + '<int:hotel_id>/rooms/', ListCreateHotelRoomType.as_view()),
    path('owner/' + APP_URL + 'rooms/<int:room_type_id>', ManageHotelRoomType.as_view()),
    path('owner/' + APP_URL + '<int:hotel_id>/reservations', ListCreateOwnerReservationView.as_view()),
    path('owner/reservations/<int:reservation_id>', ManageOwnerReservationView.as_view())
]
