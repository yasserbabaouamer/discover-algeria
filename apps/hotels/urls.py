from django.urls import path

from .views import *

APP_URL = 'hotels/'

urlpatterns = [
    path(APP_URL + 'top/', GetTopHotelsView.as_view()),
    path(APP_URL + '<int:hotel_id>/', GetHotelDetailsView.as_view()),
    path(APP_URL + '<int:hotel_id>/reviews/', ListCreateHotelReviewView.as_view()),
    path(APP_URL + '<int:hotel_id>/rooms', GetHotelAvailableRoomTypes.as_view()),
    path(APP_URL + 'reserve/', CreateReservationView.as_view()),
    path('payment/config/', GetStripPublicKey.as_view()),
    path('payment/create-payment-intent/', CreatePaymentIntentView.as_view()),
    path('payment/verify/', VerifyPaymentView.as_view()),
    path('cities/<int:city_id>/hotels', FindHotelsByCity.as_view()),
    path(APP_URL + 'amenities/', GetAllAmenities.as_view()),
    path('owner/dashboard/', GetOwnerDashboardInfo.as_view()),
    path('owner/' + APP_URL, ListCreateOwnerHotelView.as_view()),
    path('owner/' + APP_URL + '<int:hotel_id>/edit-info/', GetHotelEditInformation.as_view()),
    path('owner/' + APP_URL + 'create-info/', GetHotelCreateInformation.as_view()),
    path('owner/' + APP_URL + '<int:hotel_id>/', ManageOwnerHotelDetailsView.as_view()),
    path('owner/' + APP_URL + '<int:hotel_id>/rooms/', ListCreateRoomType.as_view()),
    path('owner/' + APP_URL + 'rooms/create-info/', GetCreateRoomInformation.as_view()),
    path('owner/' + APP_URL + 'rooms/<int:room_type_id>/edit-info/', GetEditRoomInformation.as_view()),
    path('owner/' + APP_URL + 'rooms/<int:room_type_id>/', ManageHotelRoomType.as_view()),
    path('owner/' + APP_URL + 'reservations/', ListCreateOwnerReservationView.as_view()),
    path('owner/reservations/<int:reservation_id>', ManageOwnerReservationView.as_view())
]
