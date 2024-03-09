from django.db import models
from django.db.models import CheckConstraint, Q

from apps.destinations.models import Country
from apps.users.enums import Currency
from apps.users.models import User


class Owner(models.Model):
    user = models.OneToOneField(User, related_name='owner', on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True)
    country = models.ForeignKey(Country, related_name='owners', on_delete=models.CASCADE, null=True)
    profile_pic = models.URLField(null=True)
    preferred_currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.DZD.value)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    constraints = [
        CheckConstraint(
            check=Q(preferred_currency__in=list(Currency)), name='chk_pref_currency'
        )
    ]
