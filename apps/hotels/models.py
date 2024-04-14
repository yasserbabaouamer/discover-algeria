from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, Q, Index, Count, Avg, Min, QuerySet, Func, FloatField, F, Value, Case, \
    When, BooleanField
from rest_framework.exceptions import NotFound, ValidationError

from . import managers
from apps.destinations.models import City, Country
from apps.guests.models import Guest
from apps.hotels.enums import ReservationStatus


class LevenshteinRatio(Func):
    function = "_levenshtein_ratio"
    output_field = FloatField()


class AmenityCategoryManager(models.Manager):
    pass


class AmenityCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='hotels/', null=True)
    objects = AmenityCategoryManager()

    class Meta:
        db_table = 'amenity_categories'


class Amenity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='hotels/', null=True)
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

    def find_by_id(self, hotel_id: int):
        try:
            return self.annotate(
                number_of_reviews=Count('reservations__review'),
                avg_ratings=Count('reservations__review__rating')
            ).get(pk=hotel_id)
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No Such Hotel with this id'})

    def find_by_keyword(self, keyword):
        result = self.annotate(
            name_ratio=Case(
                When(name__icontains=keyword, then=1),
                default=LevenshteinRatio(F('name'), Value(keyword)),
                output_field=FloatField(),
            )
        ).filter(
            Q(name_ratio__gt=0.3)
        ).order_by('-name_ratio')
        return result.all()

    def find_available_hotels_by_city_id(self, city_id, check_in: datetime, check_out: datetime,
                                         price_starts_at: int, price_ends_at: int):
        hotels = self.annotate(
            number_of_reviews=Count('reservations__review'),
            avg_ratings=Avg('reservations__review__rating'),
            starts_at=Min('room_types__price_per_night')
        ).filter(city_id=city_id, starts_at__gte=price_starts_at, starts_at__lte=price_ends_at).all()
        print("City hotels ", hotels)
        available_hotels = []
        for hotel in hotels.all():
            for room_type in hotel.room_types.all():
                available_rooms = Room.objects.get_available_rooms_by_room_type(room_type.id, check_in, check_out)
                if available_rooms.count() > 0:
                    available_hotels.append(hotel)
                break
        return available_hotels

    def has_amenity(self, hotel_id, amenity: str) -> bool:
        return self.filter(
            Q(id=hotel_id) &
            Q(room_types__amenities__name=amenity) | Q(amenities__name=amenity)
        ).exists()


def find_top_hotels_by_city_id(self, city_id: int):
    return (self.annotate(
        number_of_reviews=Count('reservations__review'),
        avg_ratings=Avg('reservations__review__rating'),
        starts_at=Min('room_types__price_per_night')
    ).filter(city_id=city_id).order_by('-number_of_reviews').all())


class Hotel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)  # Assuming a reasonable length for the name
    stars = models.IntegerField()
    address = models.CharField(max_length=255)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    website_url = models.URLField(null=True)
    cover_img = models.ImageField(upload_to='hotels/', null=True)
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
    img = models.ImageField(upload_to='hotels/', null=True)

    class Meta:
        db_table = 'hotel_images'


class BedType(models.Model):
    name = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='hotels/', null=True)

    class Meta:
        db_table = 'bed_types'


class RoomTypeManager(models.Manager):
    def find_by_id(self, room_type_id):
        try:
            return self.get(pk=room_type_id)
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No Such Room Type with this id'})

    def get_categories_and_amenities(self, room_type_id):
        # Get the RoomType instance based on the provided ID
        room_type = self.find_by_id(room_type_id)
        # Access the related amenities using the amenities attribute
        amenities = room_type.amenities.all()
        # Retrieve the categories of those amenities and their associated amenities
        categories = {}
        for amenity in amenities:
            category = amenity.category
            if category not in categories:
                categories[category] = []
            categories[category].append(amenity)

        return categories


class RoomType(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated unique identifier
    name = models.CharField(max_length=255)
    size = models.FloatField()  # Assuming size refers to area in square units
    nb_beds = models.PositiveIntegerField()  # Positive integer for number of beds
    main_bed_type = models.ForeignKey(BedType, on_delete=models.SET_NULL, null=True)  #
    price_per_night = models.BigIntegerField()
    cover_img = models.ImageField(upload_to='hotels/', null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    amenities = models.ManyToManyField(Amenity, db_table='room_type_amenities')  #
    objects = RoomTypeManager()

    class Meta:
        db_table = 'room_types'


class RoomTypePolicy(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, related_name='policy')
    name = models.CharField(max_length=255)
    free_cancellation_days = models.IntegerField()
    breakfast_included = models.BooleanField()
    prepayment_required = models.BooleanField()

    class Meta:
        db_table = 'room_type_policy'


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.IntegerField()
    description = models.CharField(max_length=255, null=True)
    number_of_guests = models.PositiveIntegerField()
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    objects = managers.RoomManager()

    class Meta:
        db_table = 'rooms'


class ReservationManager(models.Manager):

    def create_reservation(self, guest: Guest, first_name, last_name, email, country,
                           phone, check_in: datetime, check_out: datetime, total_price, hotel):
        return self.create(
            guest=guest,
            first_name=first_name,
            last_name=last_name,
            email=email,
            countr=country,
            phone=phone,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            hotel=hotel,
            status=ReservationStatus.ACCEPTED.value
        )


class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    guest = models.ForeignKey(Guest, related_name='reservations', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    phone = models.PositiveIntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    total_price = models.BigIntegerField()
    status = models.CharField(max_length=50, choices=ReservationStatus.choices,
                              default=ReservationStatus.ACCEPTED.value)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, related_name='reservations')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    objects = ReservationManager()

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

    def clean(self):
        if self.reservation.hotel != self.room_type.hotel:
            raise ValidationError({
                'detail': 'One of your selected room types does not have'
                          ' the same hotel as what you specified in the '
                          'request'})

    class Meta:
        db_table = 'reserved_room_types'


class RoomAssignment(models.Model):
    reserved_room_type = models.ForeignKey(ReservedRoomType, on_delete=models.CASCADE, related_name='assigned_rooms')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='assignments')

    class Meta:
        db_table = 'room_assignments'


class GuestReviewManager(models.Manager):

    def get_reviews_by_hotel_id(self, hotel_id):
        return self.annotate(
            number_of_reviews=Count('id'),
            avg_ratings=Avg('rating')
        ).filter(reservation__hotel_id=hotel_id).all()


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
