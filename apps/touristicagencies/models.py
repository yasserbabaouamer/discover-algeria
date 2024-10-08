from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q, Func, F, BigIntegerField, FloatField, Value, CheckConstraint, Count, Avg, Case, When, \
    Sum
from django.db.models.functions import Coalesce
from django.utils.dates import WEEKDAYS
from sql_util.aggregates import SubqueryCount, SubqueryAvg

from apps.users.models import User
from .enums import TourStatus, ScheduledTourStatus
from ..destinations.models import Country, City
from ..guests.models import Guest
from ..hotels.enums import ReservationStatus


class LevenshteinRatio(Func):
    function = "_levenshtein_ratio"
    output_field = FloatField()


class TouristicAgencyManager(models.Manager):

    def find_by_keyword(self, keyword: str):
        return self.annotate(
            name_ratio=Case(
                When(name__icontains=keyword, then=1),
                default=LevenshteinRatio(F('name'), Value(keyword)),
                output_field=FloatField(),
            )
        ).filter(name_ratio__gt=0.3).order_by('-name_ratio').all()


class TouristicAgency(models.Model):
    user = models.OneToOneField(User, related_name='agency', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=300)
    address = models.CharField(max_length=300, null=True)
    city = models.ForeignKey(City, related_name='touristic_agencies', on_delete=models.SET_NULL, null=True)
    website_url = models.URLField(null=True)
    cover_img = models.ImageField(null=True, upload_to='tourism_agencies/agencies/')
    objects = TouristicAgencyManager()

    class Meta:
        db_table = 'touristic_agencies'


class Guide(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255)
    contact = models.CharField(max_length=50)
    touristic_agency = models.ForeignKey(TouristicAgency, related_name='guides',
                                         on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'guides'


class PeriodicTourManager(models.Manager):

    def find_top_tours(self):
        return list(self.annotate(
            reviews_count=Coalesce(Sum('scheduled_tours__registrations__review'), Value(0),
                                   output_field=models.IntegerField()),
            rating_avg=Coalesce(Sum('scheduled_tours__registrations__review__rating'), Value(0),
                                output_field=models.IntegerField()),
        ).all()[:8])

    def find_by_keyword(self, keyword: str):
        return self.annotate(
            title_ratio=Case(
                When(title__icontains=keyword, then=1),
                default=LevenshteinRatio(F('title'), Value(keyword)),
                output_field=FloatField(),
            )
        ).filter(title_ratio__gt=0.3).order_by('-title_ratio').all()

    def find_top_tours_by_city_id(self, city_id: int):
        return self.annotate(
            reviews_count=SubqueryCount('scheduled_tours__registrations__review'),
            rating_avg=Coalesce(
                SubqueryAvg('scheduled_tours__registrations__review__rating'),
                Value(0))
        ).filter(
            city_id=city_id,
        ).all()

    def find_available_tours_by_city_id(self, city_id, days: dict):
        (self.filter(
            Q(city_id=city_id) &
            Q(start_day__in=days.keys(), end_day__in=days.keys()) &
            Q(scheduled_tours__tour_date__in=days.values(),
              scheduled_tours__tour_status__ne=ScheduledTourStatus.CANCELLED.value),
        ).annotate(
            reviews_count=SubqueryCount('scheduled_tours__registrations__review'),
            rating_avg=Coalesce(
                SubqueryAvg('scheduled_tours__registrations__review__rating'),
                Value(0))
        ).all())

    def find_by_id(self, tour_id):
        return self.annotate(
            reviews_count=SubqueryCount('scheduled_tours__registrations__review'),
            rating_avg=Coalesce(SubqueryAvg('scheduled_tours__registrations__review__rating'), Value(0))
        ).select_related('touristic_agency').get(pk=tour_id)


class PeriodicTour(models.Model):
    touristic_agency = models.ForeignKey(TouristicAgency, on_delete=models.SET_NULL, null=True, related_name='tours')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='periodic_tours')
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    cover_img = models.ImageField(null=True, upload_to='tourism_agencies/periodic_tours/')
    start_day = models.CharField(max_length=255, choices=list(WEEKDAYS.items()))
    start_time = models.TimeField()
    end_day = models.CharField(max_length=255, choices=list(WEEKDAYS.items()))
    end_time = models.TimeField()
    price = models.BigIntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
    tour_status = models.CharField(max_length=25, choices=TourStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PeriodicTourManager()

    class Meta:
        db_table = 'periodic_tours'
        constraints = [
            CheckConstraint(
                check=Q(tour_status__in=list(TourStatus)), name='chk_periodic_tour_status'
            )
        ]


class TourImage(models.Model):
    tour = models.ForeignKey(PeriodicTour, related_name='images', on_delete=models.SET_NULL, null=True)
    image = models.ImageField()

    class Meta:
        db_table = 'periodic_tour_images'


class ScheduledTour(models.Model):
    periodic_tour = models.ForeignKey(PeriodicTour, related_name='scheduled_tours',
                                      on_delete=models.SET_NULL, null=True)
    tour_date = models.DateField(unique=True)
    tour_status = models.CharField(max_length=50, choices=ScheduledTourStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scheduled_tours'
        constraints = [
            CheckConstraint(
                check=Q(tour_status__in=list(ScheduledTourStatus)), name='chk_scheduled_tour_status'
            )
        ]


class PeriodicTourRegistration(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.SET_NULL, null=True, related_name='tour_registrations')
    scheduled_tour = models.ForeignKey(ScheduledTour, related_name='registrations', on_delete=models.SET_NULL,
                                       null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    country = models.ForeignKey(Country, related_name='tour_registrations', on_delete=models.SET_NULL, null=True)
    country_code = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    phone = models.BigIntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
    status = models.CharField(max_length=50, choices=ReservationStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'periodic_tour_registrations'
        constraints = [
            CheckConstraint(
                check=Q(status__in=list(ReservationStatus)), name='chk_tour_reg_status'
            )
        ]


class PeriodicTourReview(models.Model):
    registration = models.OneToOneField(PeriodicTourRegistration, on_delete=models.SET_NULL,
                                        null=True, related_name='review')
    title = models.CharField(max_length=255)
    description = models.TextField()
    rating = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'periodic_tour_reviews'
