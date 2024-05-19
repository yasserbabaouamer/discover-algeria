from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, Q, Value

from apps.destinations.models import Country
from apps.users.enums import Currency, AccountStatus
from apps.users.models import User


class GuestManager(models.Manager):
    def create_guest(self, user: User, first_name, last_name, profile_pic=None):
        guest = self.create(user=user, first_name=first_name, last_name=last_name, profile_pic=profile_pic)
        return guest

    def find_guest_profile(self, guest_id):
        return self.annotate(
            overall_rating=Value(0)
        ).get(pk=guest_id)


class Guest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guest')
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    birthday = models.DateField(null=True)
    address = models.CharField(max_length=255, null=True)
    country_code = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    phone = models.PositiveIntegerField(validators=[RegexValidator(regex="^\d{7,15}$")], null=True)
    country = models.ForeignKey(Country, related_name='guests', on_delete=models.SET_NULL, null=True)
    profile_pic = models.ImageField(upload_to='guests/', null=True)
    about = models.TextField(null=True)
    preferred_currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.DZD.value)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    objects = GuestManager()

    class Meta:
        db_table = 'guests'

        constraints = [
            CheckConstraint(
                check=Q(preferred_currency__in=list(Currency)), name='chk_pref_currency'
            ),
            CheckConstraint(
                check=Q(status__in=list(AccountStatus)), name='chk_guest_status'
            )
        ]
