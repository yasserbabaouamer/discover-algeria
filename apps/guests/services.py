from datetime import timedelta
from datetime import timedelta
from threading import Thread

from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import Guest, User
from apps.users.services import generate_and_send_confirmation_code


def authenticate_guest(login_request: dict) -> dict | None:
    user: User = authenticate(email=login_request['email'], password=login_request['password'])
    if user is not None:
        if user.is_active:
            return generate_tokens_for_guest(user)
        else:
            Thread(target=generate_and_send_confirmation_code, args=(user,)).start()
            return None
    raise AuthenticationFailed({'detail': 'Authentication failed , invalid information'})


def generate_access_token(user: User):
    access_token = AccessToken.for_user(user)
    access_token.set_exp((access_token.current_time + timedelta(minutes=10)).isoformat())
    access = {
        'access': str(access_token)
    }
    return access


def generate_tokens_for_guest(user: User):
    refresh_token = RefreshToken.for_user(user)
    tokens = {
        'access': str(refresh_token.access_token),
        'refresh': str(refresh_token),
        'has_guest_acc': user.has_guest_account()
    }
    return tokens


def setup_guest_profile(user: User, profile_request: dict):
    guest, created = Guest.objects.get_or_create(
        user=user, defaults={
            'first_name': profile_request['first_name'],
            'last_name': profile_request['last_name'],
            'profile_pic': profile_request['profile_pic']
        }
    )
    return created
