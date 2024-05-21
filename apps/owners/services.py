from threading import Thread

from django.contrib.auth import authenticate, password_validation
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError, APIException
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.services import generate_and_send_confirmation_code
from core.utils import CustomException
from .dtos import *
from .models import Owner
from ..destinations.models import Country
from ..users.enums import AccountStatus


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
        raise CustomException(
            {'detail': 'You have already set your owner account, go to your profile settings and edit'},
            status.HTTP_409_CONFLICT)
    owner = Owner.objects.create(
        user=user,
        first_name=data['first_name'],
        last_name=data['last_name'],
        birthday=data['birthday'],
        country_code=Country.objects.find_by_id(data['country_code_id']),
        phone=data['phone'],
        country=Country.objects.find_by_id(data['country_id']),
        profile_pic=data.get('profile_pic', 'users/defaults/default_profile_pic.png'),
    )


def find_owner_essentials_info(_id):
    return get_object_or_404(Owner, pk=_id)


def find_owner_profile(owner_id):
    return Owner.objects.find_profile_by_id(owner_id)


def find_all_owners():
    return Owner.objects.filter(status=AccountStatus.ACTIVE).all()


def delete_owner(owner_id):
    owner = get_object_or_404(Owner, id=owner_id)
    owner.status = AccountStatus.DELETED_BY_ADMIN
    owner.save()


def create_owner(data: dict):
    with transaction.atomic():
        user, created = User.objects.get_or_create(email=data['email'])
        if created:
            try:
                password_validation.validate_password(data['password'])
            except Exception as e:
                raise CustomException({'detail': 'Make sure that ur password contains 8 characters and numbers'},
                                      status=status.HTTP_400_BAD_REQUEST)
            user.set_password(data['password'])
            user.save()
        if user.has_owner_account():
            raise CustomException({'detail': 'This user has already an owner account'},
                                  status=status.HTTP_409_CONFLICT)
        Owner.objects.create(
            user=user,
            first_name=data['first_name'],
            last_name=data['last_name'],
            country_code_id=data.get('country_code_id', None),
            phone=data.get('phone', None),
            country_id=data.get('country_id', None),
            birthday=data.get('birthday', None),
            profile_pic='users/defaults/default_profile_pic.png'
        )


def update_owner(owner_id, form: dict):
    data = form['body']
    owner = get_object_or_404(Owner, pk=owner_id)
    with transaction.atomic():
        for field, info in data.items():
            print(field, ': ', info)
            setattr(owner, field, info if info else None)
        if form.get('profile_pic', None):
            owner.profile_pic = form['profile_pic']
        owner.save()
