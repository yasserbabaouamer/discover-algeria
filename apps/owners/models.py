from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, Q

from apps.destinations.models import Country
from apps.users.enums import Currency
from apps.users.models import User


class OwnerManager(models.Manager):
    def create_owner(self, user, first_name, last_name, birthday, country_code, phone, country):
        return self.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            country_code=country_code,
            phone=phone,
            country=country
        )


class Owner(models.Model):
    user = models.OneToOneField(User, related_name='owner', on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birthday = models.DateField(auto_now=True)
    country_code = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    phone = models.PositiveIntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
    country = models.ForeignKey(Country, related_name='owners', on_delete=models.CASCADE, null=True)
    profile_pic = models.ImageField(upload_to='hotels/', null=True)
    preferred_currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.DZD.value)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = OwnerManager()

    class Meta:
        db_table = 'owners'
        constraints = [
            CheckConstraint(
                check=Q(preferred_currency__in=list(Currency)), name='chk_pref_currency_owners'
            )
        ]
