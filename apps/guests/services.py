from datetime import timedelta
from datetime import timedelta
from threading import Thread

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .dtos import GuestTokens
from .models import Guest, User
from apps.users.services import generate_and_send_confirmation_code


def authenticate_guest(login_request: dict) -> GuestTokens | None:
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


def generate_tokens_for_guest(user: User) -> GuestTokens:
    refresh_token = RefreshToken.for_user(user)
    return GuestTokens(
        str(refresh_token.access_token),
        str(refresh_token),
        user.has_guest_account()
    )


def setup_guest_profile(user: User, profile_request: dict):
    guest, created = Guest.objects.get_or_create(
        user=user, defaults={
            'first_name': profile_request['first_name'],
            'last_name': profile_request['last_name'],
            'profile_pic': profile_request.get('profile_pic', 'users/defaults/default_profile_pic.png')
        }
    )
    return created


def find_guest_by_id(guest_id):
    return get_object_or_404(Guest, pk=guest_id)


def find_guest_profile(guest_id):
    return Guest.objects.find_guest_profile(guest_id)
