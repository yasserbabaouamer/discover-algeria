from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import *

urlpatterns = [
    path('auth/exists/', IsEmailExistView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/confirm/', ConfirmationView.as_view()),
    path('auth/confirm/resend/', ResendConfirmationView.as_view()),
    path('auth/password-reset/', ResetPasswordView.as_view()),
    path('auth/password-reset/verify/', VerifyResetPasswordView.as_view()),
    path('auth/password-reset/complete/', CompletePasswordResetView.as_view()),
]
