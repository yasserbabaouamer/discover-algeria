from threading import Thread

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.services import generate_and_send_confirmation_code
from .dtos import *
from .models import Owner
from ..destinations.models import Country


def authenticate_owner(login_request: dict) -> OwnerTokens | None:
    user: User = authenticate(email=login_request['email'], password=login_request['password'])
    if user is not None:
        if user.is_active:
            return generate_tokens_for_owner(user)
        else:
            Thread(target=generate_and_send_confirmation_code, args=(user,)).start()
            return None
    raise AuthenticationFailed({'detail': 'Authentication failed, invalid information'})


def generate_tokens_for_owner(user: User) -> OwnerTokens:
    refresh_token = RefreshToken.for_user(user)
    return OwnerTokens(
        access=str(refresh_token.access_token),
        refresh=str(refresh_token),
        has_owner_acc=user.has_owner_account()
    )


def setup_owner_profile(user: User, data: dict):
    if user.has_owner_account():
        raise ValidationError(
            {'detail': 'You have already set your owner account, go to your profile settings and edit'})
    owner = Owner.objects.create_owner(
        user=user,
        first_name=data['first_name'],
        last_name=data['last_name'],
        birthday=data['birthday'],
        country_code=Country.objects.find_by_id(data['country_code_id']),
        phone=data['phone'],
        country=Country.objects.find_by_id(data['country_id']),
        profile_pic=data.get('cover_img', 'users/defaults/default_profile_pic.png'),
    )
