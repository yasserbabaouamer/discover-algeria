from django.contrib import admin
from django.urls import path, include

BASE_URL = 'api/v1/'
urlpatterns = [
    path(BASE_URL, include('apps.users.urls')),
    path(BASE_URL, include('apps.destinations.urls')),
    path(BASE_URL, include('apps.hotels.urls')),
]
