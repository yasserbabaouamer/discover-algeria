from enum import Enum

from django.db import models


class ReservationStatus(models.TextChoices):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REFUSED = 'Refused'
    CANCELLED_BY_OWNER = 'Cancelled_By_Owner'
    CANCELLED_BY_GUEST = 'Cancelled_By_Guest'
    COMPLETED = 'Completed'
    DELETED_BY_ADMIN = 'Deleted_By_Admin'
