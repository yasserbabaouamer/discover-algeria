import secrets
import uuid
from datetime import datetime, timedelta
from threading import Thread

import rest_framework
from decouple import config
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import User, Activation
from apps.guests.models import Guest


def authenticate_guest(login_request: dict):
    user: User = authenticate(email=login_request['email'], password=login_request['password'])
    if user is not None:
        return generate_tokens_for_guest(user)
    else:
        return None


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
        'refresh': str(refresh_token)
        # 'has_guest_acc': bool(user.guest)
    }
    return tokens


def register_new_user(signup_request: dict):
    email = signup_request['email']
    if is_email_already_exists(email):
        raise ValidationError(detail={'msg': 'This email is already exists'})
    try:
        password_validation.validate_password(signup_request['password'])
    except Exception as error:
        raise rest_framework.exceptions.ValidationError(detail=error)

    with transaction.atomic():
        user = User.objects.create_user(
            signup_request['email'],
            signup_request['password']
        )
        activation = generate_confirmation_code(user)
        Thread(target=send_confirmation_code, args=(user.email, activation.activation_code)).start()
        return activation.token


def setup_guest_profile_for_existing_user(user: User, profile_request: dict):
    guest = Guest.objects.create_guest(
        user, profile_request['first_name'], profile_request['last_name']
    )


def is_email_already_exists(email: str):
    return User.objects.is_email_already_exists(email)


def generate_confirmation_code(user) -> Activation:
    _random = secrets.randbelow(1000000)
    user_token = uuid.uuid4()
    expires_at = datetime.now() + timedelta(minutes=10)
    if Activation.objects.filter(activation_code=_random, expires_at__gt=datetime.now()).exists():
        generate_confirmation_code(user)
    activation, created = Activation.objects.get_or_create(user=user, defaults={
        'activation_code': _random,
        'token': user_token,
        'expires_at': expires_at
    })
    if not created:
        activation.activation_code = _random
        activation.token = user_token
        activation.expires_at = expires_at
        activation.save()
    return activation


def send_confirmation_code(email, code):
    subject = 'Email Verification Code'
    message = f'Your verification code is: {str(code)}'
    from_email = config('EMAIL_ADDRESS')
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def activate_user(confirmation_request: dict):
    try:
        user = User.objects.get(activation__token=str(confirmation_request['token']))
        print(user.email)
        if (user.activation.activation_code == confirmation_request['confirmation_code']
                and not user.activation.is_expired()
                and not user.activation.is_used):
            with transaction.atomic():
                user.is_active = True
                user.save()
                user.activation.is_used = True
                user.activation.save()
                return generate_tokens_for_guest(user)
        else:
            raise ValidationError({'detail': 'Invalid confirmation code'})
    except ObjectDoesNotExist as e:
        raise ValidationError({'detail': e})


def resend_confirmation_code(resend_request: dict):
    try:
        user = User.objects.get(activation__token=resend_request['token'])
        if user.is_active:
            raise ValidationError({'detail': 'Your account is already activated'})
        activation = generate_confirmation_code(user)
        Thread(target=send_confirmation_code, args=(user.email, activation.activation_code)).start()
        return activation.token
    except ObjectDoesNotExist as e:
        raise ValidationError({'detail': 'Invalid token'})


def is_email_exists(email_request: dict):
    return User.objects.is_email_already_exists(email_request['email'])
