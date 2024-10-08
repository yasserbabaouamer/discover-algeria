from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, Q, Index, Count, Avg, Min, QuerySet, Func, FloatField, F, Value, Case, \
    When, Sum, OuterRef, Subquery, ExpressionWrapper, Prefetch, IntegerField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, ValidationError
from sql_util.aggregates import SubqueryAggregate, SubqueryCount, SubqueryAvg, SubquerySum, SubqueryMin

from apps.destinations.models import City, Country
from apps.guests.models import Guest
from apps.hotels.enums import ReservationStatus, HotelCancellationPolicy, ParkingType, HotelPrepaymentPolicy, \
    HotelStatus, \
    RoomTypeEnum, RoomTypeStatus, RoomTypeCancellationPolicy, RoomTypePrepaymentPolicy, RoomStatus
from . import managers
from ..owners.models import Owner


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


class AmenityManager(models.Manager):

    def find_amenities_by_hotel_id(self, hotel_id):
        hotel = Hotel.objects.find_by_id(hotel_id)
        return self.annotate(
            checked=Case(
                When(id__in=hotel.amenities.values_list('id', flat=True), then=True),
                default=False
            )
        ).filter(category__name='Facilities').all()

    def find_all_rooms_amenities(self):
        return self.filter(~Q(category__name='Facilities'))

    def find_amenities_by_room_type_id(self, room_type_id):
        room_type = RoomType.objects.find_by_id(room_type_id)
        return self.annotate(
            checked=Case(
                When(id__in=room_type.amenities.values_list('id', flat=True), then=True),
                default=False
            )
        ).filter(~Q(category__name='Facilities')).all()


class Amenity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='accommodations/amenities/', null=True)
    category = models.ForeignKey(AmenityCategory, related_name='amenities', on_delete=models.CASCADE)
    objects = AmenityManager()

    class Meta:
        db_table = 'amenities'


class LanguageManager(models.Manager):
    def find_languages_by_hotel_id(self, hotel_id):
        hotel = Hotel.objects.find_by_id(hotel_id)
        return self.annotate(
            checked=Case(
                When(id__in=hotel.staff_languages.values_list('id', flat=True), then=True),
                default=False
            )
        ).all()


class Language(models.Model):
    name = models.CharField(max_length=255)
    objects = LanguageManager()

    class Meta:
        db_table = 'languages'


class HotelManager(models.Manager):
    w1 = 0.4  # Rating weight
    w2 = 0.3  # Number of reviews weight
    w3 = 0.2  # Number of completed reservations
    w4 = 0.1  # Number of generated revenue

    def find_top_hotels(self) -> QuerySet:
        return self.annotate(
            reservations_count=SubqueryCount('reservations'),
            revenue=SubquerySum('reservations__total_price',
                                filter=Q(status=ReservationStatus.COMPLETED)
                                ),
            rating_avg=SubqueryAvg('reservations__review__rating'),
            reviews_count=SubqueryCount('reservations__review'),
            starts_at=SubqueryMin('room_types__price_per_night'),
            average=ExpressionWrapper(F('rating_avg') * self.w1 + F('reviews_count') * self.w2 +
                                      F('reservations_count') * self.w3 + F('revenue') * self.w4,
                                      output_field=models.FloatField())
        ).filter(status=HotelStatus.VISIBLE).order_by('-average').all()[:6]

    def find_by_id(self, hotel_id: int):
        try:
            return (self.annotate(
                rating_avg=SubqueryAvg('reservations__review__rating'),
                reviews_count=SubqueryCount('reservations__review'),
                starts_at=SubqueryMin('room_types__price_per_night'),
            ).prefetch_related('owner').get(pk=hotel_id, status=HotelStatus.VISIBLE))
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
            Q(name_ratio__gt=0.3),
            status=HotelStatus.VISIBLE
        ).order_by('-name_ratio')
        return result.all()

    def find_available_hotels_by_city_id(self, city_id, check_in: datetime, check_out: datetime,
                                         price_starts_at: int, price_ends_at: int, stars: int):
        hotels = self.annotate(
            rating_avg=SubqueryAvg('reservations__review__rating'),
            reviews_count=SubqueryCount('reservations__review'),
            starts_at=SubqueryMin('room_types__price_per_night',
                                  filter=Q(price_per_night__gte=price_starts_at,
                                           price_per_night__lte=price_ends_at)),
        ).filter(
            city_id=city_id,
            status=HotelStatus.VISIBLE,
            starts_at__gte=price_starts_at,
            starts_at__lte=price_ends_at,
        ).all()
        if stars is not None:
            hotels = hotels.filter(stars=stars)
        available_hotels = []
        for hotel in hotels.all():
            for room_type in hotel.room_types.all():
                available_rooms = Room.objects.find_available_rooms_by_room_type(room_type.id, check_in, check_out)
                if available_rooms.count() > 0:
                    available_hotels.append(hotel)
                break
        return available_hotels

    def has_amenity(self, hotel_id, price_min: int, price_max: int, amenity_id: int) -> bool:
        hotel_amenity_exists = self.filter(
            id=hotel_id,
            amenities__id=amenity_id
        ).exists()
        room_type_amenity_exists = self.filter(
            id=hotel_id,
            room_types__price_per_night__gte=price_min,
            room_types__price_per_night__lte=price_max,
            room_types__amenities__id=amenity_id
        ).exists()
        return hotel_amenity_exists or room_type_amenity_exists

    def find_top_hotels_by_city_id(self, city_id: int):
        return (self.annotate(
            rating_avg=Coalesce(SubqueryAvg('reservations__review__rating'), Value(0)),
            reviews_count=SubqueryCount('reservations__review'),
            starts_at=SubqueryMin('room_types__price_per_night'),
        ).filter(city_id=city_id, status=HotelStatus.VISIBLE).order_by('-reviews_count').all())

    def find_owner_hotels(self, owner: Owner):
        return self.filter(
            owner=owner,
            status=HotelStatus.VISIBLE
        ).annotate(
            reviews_count=SubqueryCount('reservations__review'),
            rating_avg=Coalesce(SubqueryAvg('reservations__review__rating'), Value(0)),
            reservations_count=SubqueryCount('reservations'),
            check_ins_count=SubqueryCount('reservations',
                                          filter=~Q(
                                              status__in=[ReservationStatus.ACTIVE, ReservationStatus.COMPLETED])),
            cancellations_count=SubqueryCount('reservations',
                                              filter=Q(status__in=[ReservationStatus.CANCELLED_BY_GUEST,
                                                                   ReservationStatus.CANCELLED_BY_OWNER])),
            revenue=Coalesce(SubquerySum('reservations__total_price',
                                         filter=Q(status=ReservationStatus.COMPLETED)), Value(0)),
            rooms_count=SubqueryCount('room_types__rooms',
                                      filter=Q(status=RoomStatus.VISIBLE)),
            occupied_rooms_count=SubqueryCount(
                'reservations__reserved_room_types__assigned_rooms__room_id',
                filter=Q(reserved_room_type__reservation__status=ReservationStatus.ACTIVE)
            )
        ).order_by('-revenue')

    def count_owner_profits_in(self, owner: Owner, date) -> dict:
        return self.filter(
            owner=owner,
            reservations__check_out__date=date,
            reservations__status__in=[ReservationStatus.COMPLETED]
        ).aggregate(income=Count('reservations__total_price'))

    def find_hotel_details_for_dashboard(self, hotel_id: int):
        try:
            return self.annotate(
                revenue=SubquerySum('reservations__total_price',
                                    filter=Q(status=ReservationStatus.COMPLETED)),
                reservations_count=SubqueryCount('reservations'),
                cancellations_count=SubqueryCount('reservations',
                                                  filter=Q(status__in=[ReservationStatus.CANCELLED_BY_GUEST,
                                                                       ReservationStatus.CANCELLED_BY_OWNER])),

                completed_count=SubqueryCount('reservations', filter=Q(status=ReservationStatus.COMPLETED)),
                rating_avg=SubqueryAvg('reservations__review__rating'),
                reviews_count=SubqueryCount('reservations__review'),
            ).prefetch_related(
                Prefetch('room_types',
                         queryset=RoomType.objects.filter(hotel_id=hotel_id, status=RoomTypeStatus.VISIBLE)
                         .annotate(
                             rooms_count=SubqueryCount('rooms', filter=Q(status=RoomStatus.VISIBLE)),
                             occupied_rooms_count=SubqueryCount(
                                 'reserved_room_types__assigned_rooms__room_id',
                                 filter=Q(reserved_room_type__reservation__status=ReservationStatus.ACTIVE)
                             ),
                             monthly_revenue=
                             SubqueryCount('reserved_room_types',
                                           filter=Q(reservation__status=ReservationStatus.COMPLETED) &
                                                  Q(reservation__check_out__month=datetime.today().month - 1)
                                           )
                         ))
            ).get(pk=hotel_id, status=HotelStatus.VISIBLE)
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No such hotel with this id'})

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
    contact_number = models.BigIntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
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


class BedTypeManager(models.Manager):
    def find_all_beds_for_room_type(self, room_type_id):
        # Subquery to get the quantity of beds for the specific room type
        room_type_bed_subquery = RoomTypeBed.objects.filter(
            bed_type=OuterRef('pk'),
            room_type_id=room_type_id  # Use the specific RoomType id
        ).values('quantity')[:1]
        # Query to get all BedTypes with default values for RoomTypeBed fields
        bed_types_with_defaults = BedType.objects.annotate(
            quantity=Coalesce(Subquery(room_type_bed_subquery), Value(0))
        )
        for bed_type in bed_types_with_defaults:
            print(f"Bed Type: {bed_type.name}, Quantity: {bed_type.quantity}")
        return bed_types_with_defaults


class BedType(models.Model):
    name = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='accommodations/bed_types/', null=True)
    length = models.IntegerField(null=True)
    width = models.IntegerField(null=True)
    objects = BedTypeManager()

    class Meta:
        db_table = 'bed_types'


class RoomTypeManager(models.Manager):

    def find_by_id(self, room_type_id):
        try:
            return self.annotate(
                rooms_count=Count('rooms', filter=Q(rooms__status=RoomStatus.VISIBLE))
            ).get(pk=room_type_id, status=RoomTypeStatus.VISIBLE)
        except ObjectDoesNotExist as e:
            raise NotFound({'detail': 'No such room type with this id'})

    def get_categories_and_amenities(self, room_type_id):
        room_type = self.find_by_id(room_type_id)
        # Access the related amenities using the amenities attribute
        amenities = room_type.amenities.all()
        # Retrieve the categories of those amenities and their associated amenities
        categories_dict = {}
        for amenity in amenities:
            print('amenity:', amenity.name)
            category = amenity.category
            if category not in categories_dict.keys():
                categories_dict[category] = []
            categories_dict[category].append(amenity)
        return categories_dict

    def find_room_types_by_hotel_id(self, hotel_id: int):
        room_types = self.filter(
            hotel=hotel_id,
            status=RoomTypeStatus.VISIBLE
        ).annotate(
            starts_at=Min('price_per_night'),
            rooms_count=SubqueryCount('rooms', filter=Q(status=RoomStatus.VISIBLE)),
            occupied_rooms_count=SubqueryCount(
                'reserved_room_types__assigned_rooms__room_id',
                filter=Q(reserved_room_type__reservation__status=ReservationStatus.ACTIVE)
            ),
            monthly_revenue=
            SubqueryCount('reserved_room_types',
                          filter=Q(reservation__status=ReservationStatus.COMPLETED) &
                                 Q(reservation__check_out__month=datetime.today().month - 1)
                          )
        ).all()
        # link categories with the room type
        # for room_type in room_types:
        #     room_type.categories = self.get_categories_and_amenities(room_type.id)
        return room_types

    def find_available_room_types_by_hotel_id(self, hotel_id, check_in, check_out):
        room_types = self.filter(hotel_id=hotel_id, status=RoomTypeStatus.VISIBLE).all()
        available_room_types = []
        for room_type in room_types:
            room_type.available_rooms_count = len(
                Room.objects.find_available_rooms_by_room_type(room_type.id, check_in, check_out))
            if room_type.available_rooms_count > 0:
                available_room_types.append(room_type)
        return available_room_types


class RoomType(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated unique identifier
    name = models.CharField(max_length=255, choices=RoomTypeEnum.choices)
    size = models.FloatField()  # Assuming size refers to area in square units
    number_of_guests = models.PositiveIntegerField()
    price_per_night = models.BigIntegerField()
    cover_img = models.ImageField(upload_to='accommodations/room_types/', null=True)
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

    class Meta:
        db_table = 'room_type_images'


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
    status = models.CharField(max_length=255, choices=RoomStatus.choices, default=RoomStatus.VISIBLE)
    objects = managers.RoomManager()

    class Meta:
        db_table = 'rooms'
        constraints = [
            CheckConstraint(
                check=Q(status__in=list(RoomStatus)), name='chk_room_status'
            )
        ]


class ReservationManager(models.Manager):

    def create_reservation(self, guest: Guest, first_name, last_name, email, country, country_code,
                           phone, check_in: datetime, check_out: datetime, total_price, hotel):
        return self.create(
            guest=guest, first_name=first_name, last_name=last_name, email=email, country=country,
            country_code=country_code, phone=phone, check_in=check_in, check_out=check_out, total_price=total_price,
            hotel=hotel, status=ReservationStatus.CONFIRMED.value
        )

    def find_latest_reservations_to_owner_hotel(self, owner_id):
        return self.filter(
            hotel__owner_id=owner_id
        ).order_by('-created_at')

    def find_reservations_by_filters(self, owner_id: int, filters: dict):
        qs = self.filter(
            hotel__owner_id=owner_id,
            check_in__gte=filters['check_in'],
            check_out__lte=filters['check_out'],
        )
        hotel_id = filters.pop('hotel_id', None)
        if hotel_id is not None:
            qs = qs.filter(hotel_id=hotel_id)
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
    phone = models.BigIntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
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
        ).filter(reservation__hotel_id=hotel_id).prefetch_related('reservation__guest').all()

    def get_hotel_reviews_subquery(self):
        return GuestReview.objects.filter(
            reservation__hotel=OuterRef('pk')
        ).annotate(
            rating_avg=Avg('rating'),
            reviews_count=Count('id')
        )

    def find_latest_reviews_relate_to_owner(self, owner_id):
        return self.filter(
            reservation__hotel__owner_id=owner_id
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
