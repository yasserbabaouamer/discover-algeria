from django.urls import path

from .views import *

APP_URL = 'guest/'

urlpatterns = [
    path(APP_URL + 'login/', LoginGuestView.as_view()),
    path(APP_URL + 'setup-profile/', SetupGuestProfileForExistingUser.as_view()),
    path(APP_URL + 'profile/<int:guest_id>/', ManageMyGuestProfile.as_view()),
    path(APP_URL + 'essential-info/', GetEssentialGuestInfo.as_view()),
    path('admin/guests/', ListCreateGuests.as_view()),
    path('admin/guests/<int:guest_id>', ManageGuestsView.as_view()),
]
