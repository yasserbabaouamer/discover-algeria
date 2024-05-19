from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, Q, Value
from rest_framework.exceptions import NotFound

from apps.destinations.models import Country
from apps.users.enums import Currency, AccountStatus
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

    def find_profile_by_id(self, owner_id):
        try:
            return self.annotate(
                overall_rating=Value(0)
            ).get(id=owner_id)
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No such owner with this id'})


class Owner(models.Model):
    user = models.OneToOneField(User, related_name='owner', on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birthday = models.DateField(auto_now=True)
    address = models.CharField(max_length=255, null=True)
    about = models.TextField(null=True)
    country_code = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    phone = models.PositiveIntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
    country = models.ForeignKey(Country, related_name='owners', on_delete=models.CASCADE, null=True)
    profile_pic = models.ImageField(upload_to='owners/', null=True)
    preferred_currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.DZD.value)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    objects = OwnerManager()

    class Meta:
        db_table = 'owners'
        constraints = [
            CheckConstraint(
                check=Q(preferred_currency__in=list(Currency)), name='chk_pref_currency_owners'
            ),
            CheckConstraint(
                check=Q(status__in=list(AccountStatus)), name='chk_owner_status'
            )
        ]
