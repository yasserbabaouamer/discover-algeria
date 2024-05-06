from django.urls import path
from .views import *

APP_URL = 'owner/'

urlpatterns = [
    path(APP_URL + 'login/', LoginOwnerView.as_view()),
    path(APP_URL + 'setup-profile/', SetupOwnerProfileView.as_view()),
    path(APP_URL + 'profile/', SetupOwnerProfileView.as_view()),
]
