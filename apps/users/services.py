import asyncio
import multiprocessing
import secrets
from datetime import datetime, timedelta
from multiprocessing import Process
from threading import Thread

import rest_framework
from asgiref.sync import sync_to_async
from decouple import config
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Profile, Activation
from ..guests.models import Guest


def authenticate_guest(login_request: dict):
    user: User = authenticate(email=login_request['email'], password=login_request['password'])
    if user is not None and user.guest is not None:
        return generate_jwt_tokens(user)
    else:
        return None


def generate_jwt_tokens(user: User):
    refresh_token = RefreshToken.for_user(user)
    tokens = {
        'access': str(refresh_token.access_token),
        'refresh': str(refresh_token),
        'is_activated': user.is_active
    }
    return tokens


def generate_and_send_confirmation_code(user: User):
    activation = generate_confirmation_code(user=user)
    send_confirmation_code(user.email, activation.activation_code)


def register_new_guest(signup_request: map):
    email = signup_request['email']
    if is_email_already_exists(email):
        raise ValidationError(detail='This email is already used')
    try:
        password_validation.validate_password(signup_request['password'])
    except Exception as error:
        raise rest_framework.exceptions.ValidationError(detail=error)

    with transaction.atomic():
        user = User.objects.create_user(
            signup_request['first_name'],
            signup_request['last_name'],
            signup_request['email'],
            signup_request['password']
        )
        profile = Profile.objects.create_profile(user=user)
        guest = Guest.objects.create_guest(user=user)
        Thread(target=generate_and_send_confirmation_code, args=(user,))
        return generate_jwt_tokens(user)


def is_email_already_exists(email: str):
    return User.objects.is_email_already_exists(email)


def generate_confirmation_code(user) -> Activation:
    _random = secrets.randbelow(1000000)
    expires_at = datetime.now() + timedelta(minutes=5)
    if Activation.objects.filter(activation_code=_random, expires_at__gt=datetime.now()).exists():
        generate_confirmation_code(user)
    activation, created = Activation.objects.get_or_create(user=user, defaults={
        'activation_code': _random,
        'expires_at': expires_at
    })
    if not created:
        activation.activation_code = _random
        activation.expires_at = expires_at
        activation.save()
    return activation


def send_confirmation_code(email, code):
    subject = 'Email Verification Code'
    message = f'Your verification code is: {str(code)}'
    from_email = config('EMAIL_ADDRESS')
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def activate_guest(user_id: int, confirmation_code: int):
    try:
        guest = Guest.objects.get(user_id=user_id)
        if (guest.user.activation.activation_code == confirmation_code
                and not guest.user.activation.is_expired()
                and not guest.user.activation.is_used):
            with transaction.atomic():
                guest.user.is_active = True
                guest.user.save()
                guest.user.activation.is_used = True
                guest.user.activation.save()
        else:
            raise ValidationError(detail='Invalid confirmation code')
    except ObjectDoesNotExist as e:
        raise ValidationError({'detail': e})


def resend_confirmation_code(user_id: int):
    try:
        user = User.objects.get(pk=user_id)
        if user.is_active:
            raise ValidationError(detail='Your account is already activated')
        Thread(target=generate_and_send_confirmation_code, args=(user,)).start()
    except ObjectDoesNotExist as e:
        raise ValidationError(detail='This user does not exist')
