from django.db import models


class ReservationStatus(models.TextChoices):
    CONFIRMED = 'Confirmed'
    ACTIVE = 'Active'
    CANCELLED_BY_OWNER = 'Cancelled_By_Owner'
    CANCELLED_BY_GUEST = 'Cancelled_By_Guest'
    COMPLETED = 'Completed'
    DELETED_BY_ADMIN = 'Deleted_By_Admin'


class CancellationPolicy(models.TextChoices):
    NO = 'No Cancellation Policy'
    DEPENDS = 'Cancellation Depends on Selected Room Type'
    FIXED = 'Fixed Cancellation Before'


class ParkingType(models.TextChoices):
    PRIVATE = 'Private'
    PUBLIC = 'Public'


class Prepayment(models.TextChoices):
    REQUIRED = 'Required'
    NOT_REQUIRED = 'Not Required'
    DEPENDS = 'Depends on Selected Room Type'
