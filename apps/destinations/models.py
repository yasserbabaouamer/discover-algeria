from django.db import models
from django.db.models import Q, FloatField, Func, F, Value


# Create your models here.
class LevenshteinRatio(Func):
    function = "_levenshtein_ratio"
    output_field = FloatField()


class Country(models.Model):
    name = models.CharField(max_length=255)
    flag = models.URLField(null=True)

    class Meta:
        db_table = 'countries'


class CityManager(models.Manager):

    def find_by_keyword(self, keyword: str):
        return self.annotate(
            name_ratio=LevenshteinRatio(F('name'), Value(keyword))
        ).filter(
            name_ratio__gt=0.1
        ).order_by('-name_ratio').all()


class City(models.Model):
    name = models.CharField(max_length=255)
    cover_img = models.ImageField(default='img')
    country = models.ForeignKey(Country, related_name='cities', on_delete=models.SET_NULL, null=True)
    objects = CityManager()

    class Meta:
        db_table = 'cities'
