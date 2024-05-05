from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, Q, Index, Count, Avg, Min, QuerySet, Func, FloatField, F, Value, Case, \
    When, Sum, OuterRef, Subquery, ExpressionWrapper, Prefetch, IntegerField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, ValidationError

from apps.destinations.models import City, Country
from apps.guests.models import Guest
from apps.hotels.enums import ReservationStatus, HotelCancellationPolicy, ParkingType, HotelPrepaymentPolicy, \
    HotelStatus, \
    RoomTypeEnum, RoomTypeStatus, RoomTypeCancellationPolicy, RoomTypePrepaymentPolicy
from . import managers
from ..owners.models import Owner


def create_coalesce(subquery):
    return Coalesce(Subquery(subquery), Value(0), output_field=IntegerField())


class LevenshteinRatio(Func):
    function = "_levenshtein_ratio"
    output_field = FloatField()


class AmenityCategoryManager(models.Manager):
    pass


class AmenityCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='accommodations/amenities/', null=True)
    objects = AmenityCategoryManager()

    class Meta:
        db_table = 'amenity_categories'


class Amenity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='accommodations/amenities/', null=True)
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
        reservations_subquery = Reservation.objects.get_hotel_reservations_subquery()
        # Get rating avg and reviews count
        reviews = GuestReview.objects.get_hotel_reviews_subquery()
        room_type_subquery = RoomType.objects.get_hotel_room_types_subquery()
        return self.annotate(
            reservations_count=create_coalesce(reservations_subquery.values('reservations_count')[:1]),
            revenue=create_coalesce(reservations_subquery.values('revenue')[:1]),
            rating=create_coalesce(reviews.values('rating_avg')[:1]),
            reviews_count=create_coalesce(reviews.values('reviews_count')[:1]),
            starts_at=create_coalesce(room_type_subquery.values('starts_at')[:1]),
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
                reviews_count=create_coalesce(reviews_subquery.values('reviews_count')[:1]),
                rating_avg=create_coalesce(reviews_subquery.values('rating_avg')[:1]),
                starts_at=Min('room_types__price_per_night')
            ).prefetch_related('owner').get(pk=hotel_id)
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
            reviews_count=create_coalesce(reviews_subquery.values('reviews_count')[:1]),
            rating_avg=create_coalesce(reviews_subquery.values('rating_avg')[:1]),
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
            reviews_count=create_coalesce(reviews_subquery.values('reviews_count')[:1]),
            rating_avg=create_coalesce(reviews_subquery.values('rating_avg')[:1]),
            starts_at=Min('room_types__price_per_night')
        ).filter(city_id=city_id).order_by('-reviews_count').all())

    def find_owner_hotels(self, owner: Owner):
        reservation_subquery = Reservation.objects.get_hotel_reservations_subquery()
        room_type_subquery = RoomType.objects.get_hotel_room_types_subquery()
        rating_subquery = GuestReview.objects.get_hotel_reviews_subquery()
        return self.filter(owner=owner).annotate(
            rating_avg=create_coalesce(rating_subquery.values('rating_avg')[:1]),
            reservations_count=create_coalesce(reservation_subquery.values('reservations_count')[:1]),
            check_ins_count=create_coalesce(reservation_subquery.values('check_ins_count')[:1]),
            cancellations_count=create_coalesce(reservation_subquery.values('cancellations_count')[:1]),
            revenue=create_coalesce(reservation_subquery.values('revenue')[:1]),
            occupied_rooms_count=create_coalesce(room_type_subquery.values('occupied_rooms_count')[:1])
        )

    def count_owner_profits_in(self, owner: Owner, date) -> dict:
        return self.filter(
            owner=owner,
            reservations__check_out__date=date,
            reservations__status__in=[ReservationStatus.COMPLETED]
        ).aggregate(income=Count('reservations__total_price'))

    def find_hotel_details_for_dashboard(self, hotel_id: int):
        reservations_subquery = Reservation.objects.get_hotel_reservations_subquery()
        reviews_subquery = GuestReview.objects.get_hotel_reviews_subquery()
        room_type_subquery = RoomType.objects.get_hotel_room_types_subquery()

        return self.annotate(
            reservations_count=create_coalesce(reservations_subquery.values('reservations_count')[:1]),
            cancellations_count=create_coalesce(reservations_subquery.values('cancellations_count')[:1]),
            completed_count=create_coalesce(reservations_subquery.values('completed_count')[:1]),
            revenue=create_coalesce(reservations_subquery.values('revenue')[:1]),
            rating_avg=create_coalesce(reviews_subquery.values('rating_avg')[:1])
        ).prefetch_related(
            Prefetch('room_types',
                     queryset=RoomType.objects.filter(hotel_id=hotel_id)
                     .annotate(
                         rooms_count=create_coalesce(room_type_subquery.values('rooms_count')[:1]),
                         occupied_rooms_count=create_coalesce(room_type_subquery.values('occupied_rooms_count')[:1]),
                         monthly_revenue=create_coalesce(room_type_subquery.values('monthly_revenue')[:1])
                     ))
        ).get(pk=hotel_id)

    def find_with_rules_and_parking_and_images(self, hotel_id):
        try:
            return (Hotel.objects.select_related('rules', 'parking_situation')
                    .prefetch_related('images').get(pk=hotel_id))
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No such hotel found for this id'})


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
    cover_img = models.ImageField(upload_to='accommodations/hotels/', null=True)
    business_email = models.EmailField(null=True)
    country_code = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    contact_number = models.CharField(max_length=20)
    amenities = models.ManyToManyField(Amenity, db_table='hotel_amenities')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='hotels')
    staff_languages = models.ManyToManyField(Language, db_table='hotel_staff_languages')
    parking_available = models.BooleanField(default=False)
    status = models.CharField(max_length=255, choices=HotelStatus.choices, default=HotelStatus.VISIBLE.value)
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
        constraints = [
            CheckConstraint(
                check=Q(status__in=list(HotelStatus)), name='chk_hotel_status'
            )
        ]


class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='images', on_delete=models.SET_NULL, null=True)
    img = models.ImageField(upload_to='accommodations/hotels/', null=True)

    class Meta:
        db_table = 'hotel_images'


class HotelRules(models.Model):
    hotel = models.OneToOneField(Hotel, related_name='rules', on_delete=models.SET_NULL, null=True)
    check_in_from = models.TimeField()
    check_in_until = models.TimeField()
    check_out_from = models.TimeField()
    check_out_until = models.TimeField()
    cancellation_policy = models.CharField(max_length=255, choices=HotelCancellationPolicy.choices)
    days_before_cancellation = models.PositiveIntegerField(default=0)
    prepayment_policy = models.CharField(max_length=255, choices=HotelPrepaymentPolicy.choices)

    class Meta:
        db_table = 'hotel_rules'
        constraints = [
            CheckConstraint(
                check=Q(cancellation_policy__in=list(HotelCancellationPolicy)), name='chk_cancellation_policy'
            ),
            CheckConstraint(
                check=Q(prepayment_policy__in=list(HotelPrepaymentPolicy)), name='chk_prepayment_policy'
            ),
        ]


class ParkingSituation(models.Model):
    hotel = models.OneToOneField(Hotel, on_delete=models.SET_NULL, null=True, related_name='parking_situation')
    reservation_needed = models.BooleanField(default=False)
    parking_type = models.CharField(max_length=25, choices=ParkingType.choices)

    class Meta:
        db_table = 'parking_situations'
        constraints = [
            CheckConstraint(
                check=Q(parking_type__in=list(ParkingType)), name='chk_parking_type'
            )
        ]


class BedType(models.Model):
    name = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='accommodations/hotels/bed_types/', null=True)
    length = models.IntegerField(null=True)
    width = models.IntegerField(null=True)

    class Meta:
        db_table = 'bed_types'


class RoomTypeManager(models.Manager):

    def find_by_id(self, room_type_id):
        try:
            return self.get(pk=room_type_id)
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No such room type with this id'})

    def get_categories_and_amenities(self, room_type_id):
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
        rooms_subquery = Room.objects.get_room_type_rooms_subquery()
        occupied_rooms_subquery = Reservation.objects.get_room_type_occupied_rooms_subquery()
        revenues_subquery = Reservation.objects.get_room_type_revenues_subquery(datetime.today().month - 1)
        return self.filter(
            hotel=OuterRef('pk'),
        ).annotate(
            starts_at=Min('price_per_night'),
            room_types_count=Count('id'),
            rooms_count=Subquery(rooms_subquery.values('rooms_count')[:1]),
            occupied_rooms_count=Subquery(occupied_rooms_subquery.values('occupied_rooms_count')[:1]),
            monthly_revenue=Subquery(revenues_subquery.values('monthly_revenue')[:1])
        )

    def find_room_types_by_hotel_id(self, hotel_id: int):
        rooms_subquery = Room.objects.get_room_type_rooms_subquery()
        occupied_rooms_subquery = Reservation.objects.get_room_type_occupied_rooms_subquery()
        revenues_subquery = Reservation.objects.get_room_type_revenues_subquery(datetime.today().month - 1)
        room_types = self.filter(
            hotel=hotel_id,
        ).annotate(
            starts_at=Min('price_per_night'),
            rooms_count=create_coalesce(rooms_subquery.values('rooms_count')[:1]),
            occupied_rooms_count=create_coalesce(occupied_rooms_subquery.values('occupied_rooms_count')[:1]),
            monthly_revenue=create_coalesce(revenues_subquery.values('monthly_revenue')[:1])
        ).all()
        # link categories with the room type
        for room_type in room_types:
            room_type.categories = self.get_categories_and_amenities(room_type.id)
        return room_types


class RoomType(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated unique identifier
    name = models.CharField(max_length=255, choices=RoomTypeEnum.choices)
    size = models.FloatField()  # Assuming size refers to area in square units
    number_of_guests = models.PositiveIntegerField()
    price_per_night = models.BigIntegerField()
    cover_img = models.ImageField(upload_to='accommodations/hotels/', null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    amenities = models.ManyToManyField(Amenity, db_table='room_type_amenities')
    status = models.CharField(max_length=255, choices=RoomTypeStatus.choices, default=RoomTypeStatus.VISIBLE.name)
    objects = RoomTypeManager()

    class Meta:
        db_table = 'room_types'
        constraints = [
            CheckConstraint(
                check=Q(name__in=list(RoomTypeEnum)), name='chk_room_type_name'
            ),
            CheckConstraint(
                check=Q(status__in=list(RoomTypeStatus)), name='chk_room_type_status'
            )
        ]


class RoomTypeImage(models.Model):
    room_type = models.ForeignKey(RoomType, related_name='images', on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='accommodations/room_types/')


class RoomTypeBed(models.Model):
    room_type = models.ForeignKey(RoomType, related_name='beds', on_delete=models.SET_NULL, null=True)
    bed_type = models.ForeignKey(BedType, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'room_type_beds'
        unique_together = ('room_type', 'bed_type')


class RoomTypePolicies(models.Model):
    room_type = models.OneToOneField(RoomType, on_delete=models.SET_NULL, null=True, related_name='policies')
    cancellation_policy = models.CharField(max_length=255, choices=RoomTypeCancellationPolicy.choices, null=True)
    days_before_cancellation = models.PositiveIntegerField(default=0)
    prepayment_policy = models.CharField(max_length=255, choices=RoomTypePrepaymentPolicy.choices, null=True)

    class Meta:
        db_table = 'room_type_policy'
        constraints = [
            CheckConstraint(
                check=Q(cancellation_policy__in=list(RoomTypeCancellationPolicy)),
                name='chk_room_type_cancellation_policy',
            ),
            CheckConstraint(
                check=Q(prepayment_policy__in=list(RoomTypePrepaymentPolicy)),
                name='chk_room_type_prepayment_policy',
            )
        ]


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.IntegerField(null=True)
    description = models.CharField(max_length=255, null=True)
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
        return (self.filter(
            hotel=OuterRef('pk')  # reference the PK of the outer query
        ).exclude(
            ~Q(status=ReservationStatus.DELETED_BY_ADMIN)
        ).annotate(
            reservations_count=Count('pk'),
            revenue=Sum('total_price',
                        filter=Q(status=ReservationStatus.COMPLETED.value),
                        ),
            check_ins_count=Count('pk',
                                  filter=Q(status__in=[ReservationStatus.ACTIVE, ReservationStatus.COMPLETED])
                                  ),
            cancellations_count=Count('pk',
                                      filter=Q(status__in=[ReservationStatus.CANCELLED_BY_OWNER,
                                                           ReservationStatus.CANCELLED_BY_GUEST]),
                                      ),
            completed_count=Count('pk',
                                  filter=Q(status=ReservationStatus.COMPLETED.value),
                                  # default=0
                                  )
        ))

    def find_reservations_by_hotel_id(self, hotel, filters: dict):
        qs = self.filter(
            hotel=hotel,
            check_in__gte=filters['check_in'],
            check_out__lte=filters['check_out'],
        )
        room_type = filters.pop('room_type', None)
        if room_type is not None:
            qs = qs.filter(
                reserved_room_types__room_type__name=room_type
            )
        status = filters.pop('status', None)
        if status is not None:
            qs = qs.filter(
                status=room_type
            )
        return qs.order_by(filters['sort'])

    def get_room_type_occupied_rooms_subquery(self):
        return self.filter(
            status=ReservationStatus.ACTIVE.value,
            reserved_room_types__assigned_rooms__room__room_type_id=OuterRef('pk')
        ).annotate(
            occupied_rooms_count=Count('reserved_room_types__assigned_rooms__room'),
        )

    def get_room_type_revenues_subquery(self, month: int):
        return self.filter(
            status=ReservationStatus.COMPLETED.value,
            reserved_room_types__room_type_id=OuterRef('pk')
        ).annotate(
            monthly_revenue=
            Sum('total_price', filter=Q(check_out__month=month))
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
    commission = models.BigIntegerField(null=True)
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
        unique_together = ('reservation', 'room_type')


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
