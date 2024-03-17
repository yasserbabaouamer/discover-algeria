from django.db import models


# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=255)
    flag = models.URLField(null=True)

    class Meta:
        db_table = 'countries'


class City(models.Model):
    name = models.CharField(max_length=255)
    cover_img = models.ImageField(default='img')
    country = models.ForeignKey(Country, related_name='cities', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'cities'
