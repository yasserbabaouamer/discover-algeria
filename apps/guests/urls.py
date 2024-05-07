from django.urls import path

from .views import *

APP_URL = 'guest/'

urlpatterns = [
    path(APP_URL + 'login/', LoginGuestView.as_view()),
    path(APP_URL + 'setup-profile/', SetupGuestProfileForExistingUser.as_view()),
    path(APP_URL + '<int:guest_id>/profile/', ManageMyGuestProfile.as_view()),
    path(APP_URL + 'essential-info/', GetEssentialGuestInfo.as_view()),
]
