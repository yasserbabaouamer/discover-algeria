from django.urls import path

from apps.users.views import *

urlpatterns = [
    path('auth/exists/', IsEmailExistView.as_view()),
    path('guests/login/', LoginGuestView.as_view()),
    path('guests/signup/', SignupGuestView.as_view()),
    path('guests/setup-profile/', SetupGuestProfileForExistingUser.as_view()),
    path('auth/confirm/', ConfirmationView.as_view()),
    path('auth/confirm/resend/', ResendConfirmationView.as_view()),
    path('auth/password-reset/', ResetPasswordView.as_view()),
    path('auth/password-reset/verify/', VerifyResetPasswordView.as_view()),
    path('auth/password-reset/complete/', CompletePasswordResetView.as_view()),
]
