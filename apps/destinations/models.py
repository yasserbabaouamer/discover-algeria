from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q, FloatField, Func, F, Value, Count, Case, When, Prefetch, Min
from rest_framework.exceptions import NotFound


# Create your models here.
class LevenshteinRatio(Func):
    function = "_levenshtein_ratio"
    output_field = FloatField()


class CountryManger(models.Manager):
    def find_by_id(self, country_id):
        try:
            return self.get(pk=country_id)
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No such country with this id'})


class Country(models.Model):
    name = models.CharField(max_length=255)
    flag = models.ImageField(upload_to='destinations/countries/', null=True)
    country_code = models.CharField(max_length=10, null=True)
    objects = CountryManger()

    class Meta:
        db_table = 'countries'


class CityManager(models.Manager):

    def find_by_keyword(self, keyword: str):
        return self.annotate(
            name_ratio=Case(
                When(name__icontains=keyword, then=1),
                default=LevenshteinRatio(F('name'), Value(keyword)),
                output_field=FloatField(),
            )
        ).filter(
            name_ratio__gt=0.3
        ).order_by('-name_ratio').all()

    def find_by_id(self, city_id: int):
        from apps.hotels.models import Hotel
        try:
            return self.prefetch_related(
                Prefetch('hotels',
                         queryset=Hotel.objects.filter(city_id=city_id)
                         .annotate(
                             starts_at=Min('room_types__price_per_night')
                         ))
            ).get(pk=city_id)
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No such city with this id'})

    def find_top_cities(self):
        return self.annotate(
            reservations_count=Count('hotels__reservations')
        ).order_by('-reservations_count').all()[:7]


class City(models.Model):
    name = models.CharField(max_length=255)
    cover_img = models.ImageField(upload_to='destinations/cities/', null=True)
    description = models.TextField(null=True)
    country = models.ForeignKey(Country, related_name='cities', on_delete=models.SET_NULL, null=True)
    objects = CityManager()

    class Meta:
        db_table = 'cities'


class CityImage(models.Model):
    city = models.ForeignKey(City, related_name='images', on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='destinations/cities/')

    class Meta:
        db_table = 'city_images'
