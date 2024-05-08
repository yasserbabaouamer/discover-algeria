from django.db import models


class ReservationStatus(models.TextChoices):
    CONFIRMED = 'Confirmed'
    ACTIVE = 'Active'
    CANCELLED_BY_OWNER = 'Cancelled By Owner'
    CANCELLED_BY_GUEST = 'Cancelled By Guest'
    COMPLETED = 'Completed'
    DELETED_BY_ADMIN = 'Deleted_By_Admin'


class HotelCancellationPolicy(models.TextChoices):
    NO = 'No Cancellation Policy'
    DEPENDS = 'Cancellation Depends on Selected Room Type'
    FIXED = 'Fixed Cancellation Before'


class ParkingType(models.TextChoices):
    PRIVATE = 'Private'
    PUBLIC = 'Public'


class HotelPrepaymentPolicy(models.TextChoices):
    REQUIRED = 'Required'
    NOT_REQUIRED = 'Not Required'
    DEPENDS = 'Depends on Selected Room Type'


class HotelStatus(models.TextChoices):
    VISIBLE = 'Visible'
    HIDDEN = 'Hidden'
    DELETED_BY_OWNER = 'Deleted By Owner'
    DELETED_BY_ADMIN = 'Deleted By Admin'


class SortReservations(models.TextChoices):
    NAME = 'name'
    CHECK_IN = 'check_in'
    CHECK_OUT = 'check_out'
    PRICE = 'price'
    COMMISSION = 'commission'
    STATUS = 'status'
    BOOKED_AT = 'booked_at'


class RoomTypeEnum(models.TextChoices):
    SINGLE = "Single"
    DOUBLE = "Double"
    TWIN = "Twin"
    TWIN_DOUBLE = "Twin/Double"
    TRIPLE = "Triple"
    QUADRUPLE = "Quadruple"
    SUITE = "Suite"
    FAMILY = "Family"
    STUDIO = "Studio"
    APARTMENT = "Apartment"
    DORMITORY_ROOM = "Dormitory Room"
    BED_IN_DORMITORY = "Bed in Dormitory"


class RoomTypeStatus(models.TextChoices):
    VISIBLE = 'Visible'
    HIDDEN = 'Hidden'
    DELETED_BY_OWNER = 'Deleted By Owner'


class RoomTypeCancellationPolicy(models.TextChoices):
    NO = 'No Cancellation'
    BEFORE = 'Cancellation Before'


class RoomTypePrepaymentPolicy(models.TextChoices):
    NOT_REQUIRED = 'Prepayment is not required'
    REQUIRED = 'Prepayment is required'
