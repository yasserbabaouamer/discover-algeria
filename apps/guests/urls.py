from django.urls import path

from .views import *

urlpatterns = [
    path('guests/login/', LoginGuestView.as_view()),
    path('guests/setup-profile/', SetupGuestProfileForExistingUser.as_view()),
    path('guests/<int:guest_id>/profile/', ManageMyGuestProfile.as_view()),
    path('guests/<int:guest_id>/essential-info/', GetEssentialGuestInfo.as_view()),
]
