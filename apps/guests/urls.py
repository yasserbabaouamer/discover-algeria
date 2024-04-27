from django.urls import path

from .views import *

urlpatterns = [
    path('guests/login/', LoginGuestView.as_view()),
    path('guests/setup-profile/', SetupGuestProfileForExistingUser.as_view()),
]
