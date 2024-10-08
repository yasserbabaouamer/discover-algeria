from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Index, CheckConstraint, Q
from django.utils.timezone import now
from rest_framework.exceptions import NotFound

from apps.users.enums import *


class UserManager(BaseUserManager):
    def create_user(self, email, password, is_active=False):
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.is_active = is_active
        user.save()
        return user

    def create_superuser(self, email, password):
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.is_superuser = True
        user.save()
        return user

    def is_email_already_exists(self, email: str):
        return self.filter(email=email).exists()

    def find_by_email(self, email: str):
        try:
            return self.get(email=email)
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No such user account With this email address'})


class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(max_length=255, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=AccountStatus.choices, default=AccountStatus.ACTIVE.value)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_account_status(self):
        return AccountStatus[self.status]

    def has_guest_account(self):
        try:
            return self.guest is not None
        except ObjectDoesNotExist as e:
            return False

    def has_owner_account(self):
        try:
            return self.owner is not None
        except ObjectDoesNotExist as e:
            return False

    class Meta:
        db_table = 'users'
        indexes = [
            Index(fields=('status',), name='idx_status'),
        ]
        constraints = [
            CheckConstraint(
                check=Q(status__in=list(AccountStatus)), name='chk_account_status'
            )
        ]


class ConfirmationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='activation', null=True)
    code = models.CharField(max_length=255)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return now() > self.expires_at

    class Meta:
        db_table = 'confirmation_codes'


class PasswordResetCodeManager(models.Manager):

    def find_by_token(self, token):
        try:
            return self.get(token=token)
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No such record With this provided token'})


class PasswordResetCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='password_reset', null=True)
    token = models.UUIDField(unique=True, max_length=100, null=True)
    is_token_used = models.BooleanField(default=False)
    code = models.CharField(max_length=255)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    objects = PasswordResetCodeManager()

    def is_expired(self):
        return now() > self.expires_at

    class Meta:
        db_table = 'password_reset_codes'


class Identity(models.Model):
    id_pic = models.ImageField(upload_to='users/identities/')
    status = models.CharField(max_length=10, choices=IdentityStatus.choices)

    class Meta:
        db_table = 'identities'
