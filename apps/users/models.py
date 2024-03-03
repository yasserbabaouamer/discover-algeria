from datetime import datetime, timezone

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.timezone import now

from apps.destinations.models import Country
from apps.users.enums import *


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password):
        email = self.normalize_email(email)
        user = self.model(first_name=first_name, last_name=last_name, email=email)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, first_name, last_name, email, password):
        email = self.normalize_email(email)
        user = self.model(first_name=first_name, last_name=last_name, email=email)
        user.set_password(password)
        user.is_superuser = True
        user.save()
        return user

    def is_email_already_exists(self, email: str):
        return self.filter(email=email).exists()


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=AccountStatus.choices, default=AccountStatus.ACTIVE.value)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_account_status(self):
        return AccountStatus[self.status]

    class Meta:
        db_table = 'users'


class Activation(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='activation', null=True)
    activation_code = models.IntegerField()
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return now() > self.expires_at

    class Meta:
        db_table = 'activations'




class ProfileManager(models.Manager):
    def create_profile(self, user: User, birthday=None, phone=None, country=None):
        profile = self.create(user=user, birthday=birthday, phone=phone, country=country,
                              created_at=datetime.now(), updated_at=datetime.now())
        return profile


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    birthday = models.DateField(null=True)
    phone = models.CharField(max_length=20, null=True)
    country = models.ForeignKey(Country, related_name='profiles', on_delete=models.CASCADE, null=True)
    profile_pic = models.URLField(null=True)
    preferred_currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.DZD.value)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ProfileManager()

    class Meta:
        db_table = 'profiles'


class Identity(models.Model):
    id_pic = models.URLField()
    status = models.CharField(max_length=10, choices=IdentityStatus.choices)

    class Meta:
        db_table = 'identities'
