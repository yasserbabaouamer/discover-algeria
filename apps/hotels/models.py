from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, Q, Index, Count, Avg, Min, QuerySet, Func, FloatField, F, Value, Case, \
    When, BooleanField, Sum, OuterRef, Subquery, ExpressionWrapper
from rest_framework.exceptions import NotFound, ValidationError

from . import managers
from apps.destinations.models import City, Country
from apps.guests.models import Guest
from apps.hotels.enums import ReservationStatus, CancellationPolicy, ParkingType
from ..owners.models import Owner
from ..users.models import User


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


class Language(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'languages'


class HotelManager(models.Manager):
    w1 = 0.4  # Rating weight
    w2 = 0.3  # Number of reviews weight
    w3 = 0.2  # Number of completed reservations
    w4 = 0.1  # Number of generated revenue

    def find_top_hotels(self) -> QuerySet:
        # Get reservations count and sum of total price
        reservations = Reservation.objects.get_hotel_reservations_subquery()
        # Get rating avg and reviews count
        reviews = GuestReview.objects.get_hotel_reviews_subquery()
        starts_at = RoomType.objects.get_hotel_room_types_subquery()
        return self.annotate(
            reservations_count=Subquery(reservations.values('reservation_count')[:1]),
            revenue=Subquery(reservations.values('revenue')[:1]),
            rating=Subquery(reviews.values('rating_avg')[:1]),
            reviews_count=Subquery(reviews.values('reviews_count')[:1]),
            starts_at=Subquery(starts_at),
            average=ExpressionWrapper(F('rating') * self.w1 + F('reviews_count') * self.w2 +
                                      F('reservations_count') * self.w3 + F('revenue') * self.w4,
                                      output_field=models.FloatField())
        ).order_by('-average').all()

    def find_by_id(self, hotel_id: int):
        try:
            # Get rating avg and reviews count
            reviews_subquery = GuestReview.objects.get_hotel_reviews_subquery()
            lowest_price_subquery = RoomType.objects.get_hotel_room_types_subquery()
            return self.annotate(
                reviews_count=Subquery(reviews_subquery.values('reviews_count')[:1]),
                rating_avg=Subquery(reviews_subquery.values('rating_avg')[:1]),
                starts_at=Min('room_types__price_per_night')
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
        reviews_subquery = GuestReview.objects.get_hotel_reviews_subquery()
        lowest_price_subquery = RoomType.objects.get_hotel_room_types_subquery()
        hotels = self.annotate(
            reviews_count=Subquery(reviews_subquery.values('reviews_count')[:1]),
            rating_avg=Subquery(reviews_subquery.values('rating_avg')[:1]),
            starts_at=Min('room_types__price_per_night')
        ).filter(city_id=city_id, starts_at__gte=price_starts_at, starts_at__lte=price_ends_at).all()
        available_hotels = []
        for hotel in hotels.all():
            for room_type in hotel.room_types.all():
                available_rooms = Room.objects.find_available_rooms_by_room_type(room_type.id, check_in, check_out)
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
        reviews_subquery = GuestReview.objects.get_hotel_reviews_subquery()
        return (self.annotate(
            reviews_count=Subquery(reviews_subquery.values('reviews_count')[:1]),
            rating_avg=Subquery(reviews_subquery.values('rating_avg')[:1]),
            starts_at=Min('room_types__price_per_night')
        ).filter(city_id=city_id).order_by('-reviews_count').all())

    def find_owner_hotels(self, owner: Owner):
        reservation_subquery = Reservation.objects.get_hotel_reservations_subquery()
        room_type_subquery = RoomType.objects.get_hotel_room_types_subquery()
        rating_subquery = GuestReview.objects.get_hotel_reviews_subquery()
        return self.filter(owner=owner).annotate(
            rating_avg=Subquery(rating_subquery.values('rating_avg')[:1]),
            reservations_count=Subquery(reservation_subquery.values('reservations_count')[:1]),
            check_ins_count=Subquery(reservation_subquery.values('check_ins_count')[:1]),
            cancellations_count=Subquery(reservation_subquery.values('cancellations_count')[:1]),
            revenue=Subquery(reservation_subquery.values('revenue')[:1]),
            occupied_rooms_count=Subquery(room_type_subquery.values('occupied_rooms_count')[:1])
        )


class Hotel(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(Owner, related_name='hotels', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    stars = models.IntegerField()
    address = models.CharField(max_length=255)
    about = models.TextField(null=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    website_url = models.URLField(null=True)
    cover_img = models.ImageField(upload_to='hotels/', null=True)
    business_email = models.EmailField(null=True)
    country_code = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    contact_number = models.CharField(max_length=20)
    amenities = models.ManyToManyField(Amenity, db_table='hotel_amenities')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='hotels')
    staff_languages = models.ManyToManyField(Language, db_table='hotel_staff_languages')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
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


class HotelRule(models.Model):
    check_in = models.TimeField()
    check_out = models.TimeField()
    cancellation_policy = models.CharField(max_length=255, choices=CancellationPolicy.choices)
    days_before_cancellation = models.IntegerField(default=0)

    class Meta:
        db_table = 'hotel_rules'
        constraints = [
            CheckConstraint(
                check=Q(cancellation_policy__in=list(CancellationPolicy)), name='chk_cancellation_policy'
            )
        ]


class ParkingSituation(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, related_name='parking_situation')
    reservation_needed = models.BooleanField(default=False)
    type = models.CharField(max_length=25, choices=ParkingType.choices)

    class Meta:
        db_table = 'parking_situations'
        constraints = [
            CheckConstraint(
                check=Q(type__in=list(ParkingType)), name='chk_parking_type'
            )
        ]


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

    def get_hotel_room_types_subquery(self):
        return self.filter(
            hotel=OuterRef('pk')
        ).annotate(
            starts_at=Min('price_per_night'),
            room_types_count=Count('id'),
            occupied_rooms_count=Count('reserved_room_types__assigned_rooms__room_id',
                                       filter=Q(
                                           reserved_room_types__reservation__status=ReservationStatus.ACTIVE.value))
        )


class RoomType(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated unique identifier
    name = models.CharField(max_length=255)
    size = models.FloatField()  # Assuming size refers to area in square units
    nb_beds = models.PositiveIntegerField()  # Positive integer for number of beds
    bed_types = models.ManyToManyField(BedType, db_table='room_type_beds')
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

    def create_reservation(self, guest: Guest, first_name, last_name, email, country, country_code,
                           phone, check_in: datetime, check_out: datetime, total_price, hotel):
        return self.create(
            guest=guest, first_name=first_name, last_name=last_name, email=email, country=country,
            country_code=country_code, phone=phone, check_in=check_in, check_out=check_out, total_price=total_price,
            hotel=hotel, status=ReservationStatus.CONFIRMED.value
        )

    def get_hotel_reservations_subquery(self):
        return self.filter(
            hotel=OuterRef('pk')  # reference the PK of the outer query
        ).annotate(
            reservations_count=Count('pk', filter=Q(status=ReservationStatus.CONFIRMED.value)),
            revenue=Sum('total_price',
                        filter=Q(status=ReservationStatus.CONFIRMED.value) |
                               Q(status=ReservationStatus.ACTIVE.value) |
                               Q(status=ReservationStatus.COMPLETED.value)
                        ),
            check_ins_count=Count('pk',
                                  filter=Q(status=ReservationStatus.ACTIVE.value) |
                                         Q(status=ReservationStatus.COMPLETED.value)
                                  ),
            cancellations_count=Count('pk',
                                      filter=Q(status=ReservationStatus.CANCELLED_BY_OWNER.value) |
                                             Q(status=ReservationStatus.CANCELLED_BY_GUEST.value)
                                      )
        )


class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    guest = models.ForeignKey(Guest, related_name='reservations', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    country = models.ForeignKey(Country, related_name='reservations', on_delete=models.SET_NULL, null=True)
    country_code = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    phone = models.PositiveIntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    total_price = models.BigIntegerField()
    status = models.CharField(max_length=50, choices=ReservationStatus.choices,
                              default=ReservationStatus.CONFIRMED.value)
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
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="reserved_room_types")
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

    def get_hotel_reviews_subquery(self):
        return GuestReview.objects.filter(
            reservation__hotel=OuterRef('pk')
        ).annotate(
            rating_avg=Avg('rating'),
            reviews_count=Count('id')
        )


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
