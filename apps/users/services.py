import secrets
import uuid
from datetime import datetime, timedelta
from threading import Thread

import django.contrib.auth.password_validation
import rest_framework
from decouple import config
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .models import User, ConfirmationCode, PasswordResetCode


def generate_access_token(user: User):
    access_token = AccessToken.for_user(user)
    access_token.set_exp((access_token.current_time + timedelta(minutes=10)).isoformat())
    access = {
        'access': str(access_token)
    }
    return access


def register_new_user(signup_request: dict):
    email = signup_request['email']
    if is_email_already_exists(email):
        raise ValidationError(detail={'msg': 'This email is already exists'})
    try:
        password_validation.validate_password(signup_request['password'])
    except Exception as e:
        raise ValidationError({'detail': e})
    with transaction.atomic():
        user = User.objects.create_user(
            signup_request['email'],
            signup_request['password']
        )
        confirmation_code = generate_confirmation_code(user)
        Thread(target=send_confirmation_code, args=(user.email, confirmation_code)).start()


def is_email_already_exists(email: str):
    return User.objects.is_email_already_exists(email)


def generate_confirmation_code(user) -> int:
    code = secrets.randbelow(1000000)
    expires_at = datetime.now() + timedelta(minutes=10)
    hashed_code = make_password(str(code))
    confirmation_code, created = ConfirmationCode.objects.get_or_create(user=user, defaults={
        'code': hashed_code,
        'expires_at': expires_at
    })
    if not created:
        confirmation_code.code = hashed_code
        confirmation_code.expires_at = expires_at
        confirmation_code.save()
    return code


def send_confirmation_code(email, code):
    subject = 'Email Verification Code'
    message = f'Your verification code is: {str(code)}'
    from_email = config('EMAIL_ADDRESS')
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def generate_and_send_confirmation_code(user: User):
    confirmation_code = generate_confirmation_code(user)
    send_confirmation_code(user.email, confirmation_code)


def activate_user(confirmation_request: dict):
    user = User.objects.find_by_email(confirmation_request['email'])
    if (check_password(str(confirmation_request['confirmation_code']), user.activation.code)
            and not user.activation.is_expired()
            and not user.activation.is_used):
        with transaction.atomic():
            user.is_active = True
            user.save()
            user.activation.is_used = True
            user.activation.save()
            refresh = RefreshToken.for_user(user)
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
    else:
        raise ValidationError({'detail': 'Invalid confirmation code'})


def resend_confirmation_code(request: dict):
    user = User.objects.find_by_email(request['email'])
    if user.is_active:
        raise ValidationError({'detail': 'Your account is already activated'})
    confirmation_code = generate_confirmation_code(user)
    Thread(target=send_confirmation_code, args=(user.email, confirmation_code)).start()


def is_email_exists(email_request: dict):
    return User.objects.is_email_already_exists(email_request['email'])


"""Password Reset Methods"""


def generate_password_reset_code(user: User):
    code = secrets.randbelow(1000000)
    expires_at = datetime.now() + timedelta(minutes=15)
    hashed_code = make_password(str(code))
    password_reset, created = PasswordResetCode.objects.get_or_create(user=user, defaults={
        'code': hashed_code,
        'expires_at': expires_at
    })
    if not created:
        password_reset.code = hashed_code
        password_reset.expires_at = expires_at
        password_reset.save()
    return code


def send_password_reset_code(email, code):
    subject = 'Your Password Reset Code'
    message = f'Your password reset code is: {str(code)}'
    from_email = config('EMAIL_ADDRESS')
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def reset_password(request: dict):
    user = User.objects.find_by_email(request['email'])
    reset_code = generate_password_reset_code(user)
    Thread(target=send_password_reset_code, args=(user.email, reset_code)).start()


def generate_token_for_password_reset(confirmation_request):
    user = User.objects.find_by_email(confirmation_request['email'])
    if (check_password(str(confirmation_request['confirmation_code']), user.password_reset.code)
            and not user.password_reset.is_expired()
            and not user.password_reset.is_used):
        token = uuid.uuid4()
        user.password_reset.token = token
        user.password_reset.is_used = True
        user.password_reset.save()
        return token
    raise ValidationError({'detail': 'Invalid confirmation code or expired'})


def update_password(complete_request: dict):
    password_reset = PasswordResetCode.objects.find_by_token(complete_request['token'])
    if password_reset.is_token_used:
        raise ValidationError({'detail': 'This token has been used'})
    user = password_reset.user
    try:
        password_validation.validate_password(complete_request['new_password'])
    except Exception as e:
        raise ValidationError({'detail': e})
    user.set_password(complete_request['new_password'])
    password_reset.is_token_used = True
    user.save()
