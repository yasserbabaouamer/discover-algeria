from datetime import timedelta
from datetime import timedelta
from threading import Thread

from django.contrib.auth import authenticate, password_validation
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from core.utils import CustomException
from .dtos import GuestTokens
from .models import Guest, User
from apps.users.services import generate_and_send_confirmation_code
from ..users.enums import AccountStatus


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


def find_all_guests():
    return Guest.objects.find_all_guests_for_admin()


def delete_guest(guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    guest.status = AccountStatus.DELETED_BY_ADMIN.value
    guest.save()


def create_guest(data: dict):
    with transaction.atomic():
        user, created = User.objects.get_or_create(email=data['email'])
        if created:
            try:
                password_validation.validate_password(data['password'])
            except Exception as e:
                raise CustomException({'detail': 'Make sure that ur password contains 8 characters and numbers'},
                                      status=status.HTTP_400_BAD_REQUEST)
            user.set_password(data['password'])
            user.is_active = True
            user.save()
        if user.has_guest_account():
            raise CustomException({'detail': 'This user has already a guest account'},
                                  status=status.HTTP_409_CONFLICT)
        user.is_active = True
        user.save()
        Guest.objects.create(
            user=user,
            first_name=data['first_name'],
            last_name=data['last_name'],
            country_code_id=data.get('country_code_id', None),
            phone=data.get('phone', None),
            country_id=data.get('country_id', None),
            birthday=data.get('birthday', None),
            profile_pic='users/defaults/default_profile_pic.png'
        )


def update_guest(guest_id, form: dict):
    data = form['body']
    guest = get_object_or_404(Guest, id=guest_id)
    with transaction.atomic():
        for field, info in data.items():
            setattr(guest, field, info if info else None)
        if form.get('profile_pic', None):
            guest.profile_pic = form['profile_pic']
        guest.save()
