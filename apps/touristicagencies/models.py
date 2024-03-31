from django.db import models
from django.db.models import Q, Func, F, BigIntegerField, FloatField, Value

from apps.users.models import User
from .enums import TourStatus
from ..destinations.models import Country


class LevenshteinRatio(Func):
    function = "_levenshtein_ratio"
    output_field = FloatField()


class TouristicAgencyManager(models.Manager):

    def find_by_keyword(self, keyword: str):
        return self.annotate(
            name_ratio=LevenshteinRatio(F('name'), Value(keyword))
        ).filter(name_ratio__gt=0.1).order_by('-name_ratio').all()


class TouristicAgency(models.Model):
    user = models.OneToOneField(User, related_name='agency', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=300)
    country = models.ForeignKey(Country, related_name='touristic_agencies', on_delete=models.SET_NULL, null=True)
    website_url = models.URLField(null=True)
    cover_img = models.ImageField(null=True)
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


class TourManager(models.Manager):

    def get_top_tours(self):
        return self.all()[:5]

    def find_by_keyword(self, keyword: str):
        return self.annotate(
            title_ratio=LevenshteinRatio(Value(keyword), F('title'))
        ).filter(title_ratio__gt=0.1).order_by('-title_ratio').all()


class Tour(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    cover_img = models.ImageField(null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.IntegerField()
    tour_status = models.CharField(max_length=25, choices=TourStatus.choices, default=TourStatus.VISIBLE.value)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    touristic_agency = models.ForeignKey(TouristicAgency, on_delete=models.SET_NULL, null=True, related_name='tours')
    objects = TourManager()

    class Meta:
        db_table = 'tours'


class TourImage(models.Model):
    tour = models.ForeignKey(Tour, related_name='images', on_delete=models.SET_NULL, null=True)
    image = models.ImageField()

    class Meta:
        db_table = 'tour_images'
