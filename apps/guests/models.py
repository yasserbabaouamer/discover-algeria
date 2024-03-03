from django.db import models

from apps.users.models import User, Profile


class GuestManager(models.Manager):
    def create_guest(self, user):
        guest = self.create(user=user)
        return guest


class Guest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    objects = GuestManager()

    class Meta:
        db_table = 'guests'
