from django.urls import path
from .views import *

APP_URL = 'owner/'

urlpatterns = [
    path(APP_URL + 'login/', LoginOwnerView.as_view(), name='login-owner'),
    path(APP_URL + 'setup-profile/', SetupOwnerProfileView.as_view()),
    path(APP_URL + '<int:owner_id>/', ManageProfileView.as_view()),
    path(APP_URL + 'view-profile/<int:owner_id>/', GetOwnerProfileForAnyone.as_view()),
    path(APP_URL + 'essential-info/', GetOwnerEssentials.as_view()),
    path('admin/owners/', ListCreateOwners.as_view()),
    path('admin/owners/<int:owner_id>/', ManageOwnersView.as_view()),
]
