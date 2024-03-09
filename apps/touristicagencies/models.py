from django.db import models
from apps.users.models import User
from .enums import TourStatus


class TouristicAgency(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=300)
    user = models.OneToOneField(User, related_name='agency', on_delete=models.SET_NULL, null=True)
    website_url = models.URLField(null=True)
    cover_img = models.URLField(null=True)

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


class Tour(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.IntegerField()
    tour_status = models.CharField(max_length=25, choices=TourStatus.choices, default=TourStatus.VISIBLE.value)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    touristic_agency = models.ForeignKey(TouristicAgency, on_delete=models.SET, null=True, related_name='tours')
    objects = TourManager()

    class Meta:
        db_table = 'tours'


class TourImage(models.Model):
    tour = models.ForeignKey(Tour, related_name='images', on_delete=models.SET_NULL, null=True)
    image = models.ImageField()

    class Meta:
        db_table = 'tour_images'
