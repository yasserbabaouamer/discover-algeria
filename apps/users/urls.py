from django.urls import path

from apps.users.views import *

urlpatterns = [
    path('guests/login/', LoginGuestView.as_view()),
    path('guests/signup/', SignupGuestView.as_view()),
    path('auth/confirm/', ConfirmationView.as_view()),
    path('auth/confirm/resend', ResendConfirmationView.as_view()),
]
