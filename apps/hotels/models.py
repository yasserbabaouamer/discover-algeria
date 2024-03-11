from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import CheckConstraint, Q, Index, Count, Avg, Min, QuerySet

from apps.destinations.models import City
from apps.guests.models import Guest
from apps.hotels.enums import ReservationStatus


class AmenityCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    icon = models.URLField(null=True)

    class Meta:
        db_table = 'amenity_categories'


class Amenity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    icon = models.URLField(null=True)
    category = models.ForeignKey(AmenityCategory, related_name='amenities', on_delete=models.CASCADE)

    class Meta:
        db_table = 'amenities'


class HotelManager(models.Manager):

    def get_most_visited_hotels(self) -> QuerySet:
        return self.annotate(
            reservations_count=Count('room_types__reservations'),
            rating=Avg('room_types__reservations__review__rating'),
            starts_at=Min('room_types__price_per_night')
        ).order_by('-reservations_count')

    def get_hotel_by_id(self, hotel_id: int):
        try:
            return self.prefetch_related('room_types', 'amenities').get(pk=hotel_id)
        except ObjectDoesNotExist as e:
            return None


class Hotel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)  # Assuming a reasonable length for the name
    stars = models.IntegerField()
    address = models.CharField(max_length=255)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    website_url = models.URLField(null=True)
    cover_img = models.URLField(null=True)
    about = models.TextField(null=True)  # For longer text descriptions
    business_email = models.EmailField(null=True)
    contact_number = models.CharField(max_length=20)
    amenities = models.ManyToManyField(Amenity, db_table='hotel_amenities')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='hotels')
    objects = HotelManager()

    class Meta:
        db_table = 'hotels'
        indexes = [
            Index(fields=('name',), name='idx_name'),
            Index(fields=('address',), name='idx_address'),
            Index(fields=('latitude', 'longitude'), name='idx_location'),
        ]


class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='images', on_delete=models.SET_NULL, null=True)
    img = models.URLField(null=True)

    class Meta:
        db_table = 'hotel_images'


class BedType(models.Model):
    name = models.CharField(max_length=50)
    icon = models.URLField(null=True)

    class Meta:
        db_table = 'bed_types'


class RoomType(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated unique identifier
    name = models.CharField(max_length=255)
    size = models.FloatField()  # Assuming size refers to area in square units
    nb_beds = models.PositiveIntegerField()  # Positive integer for number of beds
    main_bed_type = models.ForeignKey(BedType, on_delete=models.SET_NULL, null=True)  #
    price_per_night = models.BigIntegerField()
    cover_img = models.URLField(max_length=2048)  # Maximum URL length
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    amenities = models.ManyToManyField(Amenity, db_table='room_type_amenities')  #

    class Meta:
        db_table = 'room_types'


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.IntegerField()
    description = models.CharField(max_length=255)
    number_of_guests = models.PositiveIntegerField()
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')

    class Meta:
        db_table = 'rooms'


class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    guest = models.ForeignKey(Guest, related_name='reservations', on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_price = models.BigIntegerField()
    status = models.CharField(max_length=50, choices=ReservationStatus.choices)

    class Meta:
        db_table = 'reservations'
        constraints = [
            CheckConstraint(
                check=Q(status__in=list(ReservationStatus)), name='chk_status'
            )
        ]


class ReservedRoomType(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="reserved_room_types")
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    nb_rooms = models.PositiveIntegerField()

    class Meta:
        db_table = 'reserved_room_types'


class RoomAssignment(models.Model):
    reserved_room_type = models.ForeignKey(ReservedRoomType, on_delete=models.CASCADE, related_name='assigned_rooms')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='assignments')

    class Meta:
        db_table = 'room_assignments'


class GuestReviewManager(models.Manager):

    def get_reviews_by_hotel_id(self, hotel_id):
        return self.filter(reservation__reserved_room_types__room_type__hotel_id=hotel_id).all()


class GuestReview(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = GuestReviewManager()

    class Meta:
        db_table = 'guest_reviews'
        indexes = [
            Index(fields=('rating',), name='idx_rating'),
            Index(fields=('created_at',), name='idx_created_at'),
        ]
