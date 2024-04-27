from django.urls import path
from .views import *

APP_URL = 'owners/'

urlpatterns = [
    path(APP_URL + 'login/', LoginOwnerView.as_view()),
    path(APP_URL + 'setup-profile/', SetupOwnerProfileView.as_view()),
]
