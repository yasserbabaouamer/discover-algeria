from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from .dtos import *
from .enums import PrepaymentPolicy, ParkingType, CancellationPolicy, SortReservations, RoomTypeEnum, ReservationStatus
from .models import Hotel, HotelImage, RoomType, Reservation, Amenity, AmenityCategory, BedType, GuestReview


class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['id', 'img']


class HotelSerializer(serializers.ModelSerializer):
    reservations_count = serializers.IntegerField()
    rating = serializers.FloatField()
    starts_at = serializers.IntegerField()
    average = serializers.FloatField()
    cover_img = HotelImageSerializer(many=True)

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'stars', 'average', 'cover_img', 'starts_at', 'reservations_count', 'rating', 'images']


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ['id', 'cover_img', 'name', 'size', 'main_bed_type', 'price_per_night', 'nb_beds', 'amenities']


class ReviewDtoSerializer(DataclassSerializer):
    class Meta:
        dataclass = ReviewDTO


class ReservationSerializer(serializers.ModelSerializer):
    review = ReviewDtoSerializer()

    class Meta:
        model = Reservation
        fields = ['review']  # Add other fields as needed


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'


class AmenityCategorySerializer(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True)

    class Meta:
        model = AmenityCategory
        fields = ['id', 'name', 'icon', 'amenities']


class HotelDetailsSerializer(DataclassSerializer):
    amenities = AmenitySerializer(many=True)

    class Meta:
        dataclass = HotelDetailsDTO


class RoomTypeRequestSerializer(serializers.Serializer):
    room_type_id = serializers.IntegerField()
    nb_rooms = serializers.IntegerField(validators=[MinValueValidator(1)])


class RoomReservationRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    country_id = serializers.IntegerField(validators=[MinValueValidator(0)])
    country_code_id = serializers.IntegerField(validators=[MinValueValidator(0)])
    phone = serializers.IntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
    hotel_id = serializers.IntegerField(validators=[MinValueValidator(0)])
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    requested_room_types = RoomTypeRequestSerializer(many=True)

    def validate(self, data):
        # Check that start_date is before end_date.
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        if check_in >= check_out:
            raise serializers.ValidationError({'detail': "End date must be after start date"})
        return data


class BedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BedType
        fields = '__all__'


class RoomTypeDtoSerializer(DataclassSerializer):
    categories = AmenityCategorySerializer(many=True)
    main_bed_type = BedTypeSerializer()

    class Meta:
        dataclass = RoomTypeDTO
        fields = ["id", "name", "size", "nb_beds", "price_per_night", "cover_img",
                  "nb_available_rooms", "main_bed_type", "categories"]


class GetHotelAvailableRoomTypesRequestSerializer(serializers.Serializer):
    check_in = serializers.DateField(required=False)
    check_out = serializers.DateField(required=False)


class FilterRequestSerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    number_of_adults = serializers.IntegerField(required=False, default=2)
    number_of_children = serializers.IntegerField(required=False, default=0)
    starts_at = serializers.IntegerField(required=False)
    ends_at = serializers.IntegerField(required=False)
    amenities = Amenity.objects.all()
    # Dynamically create serializers fields for each amenity
    amenity_map = {}
    for amenity in amenities:
        field_name = amenity.name.lower().replace(' ', '_')
        locals()[field_name] = serializers.BooleanField(required=False, default=False)
        amenity_map[field_name] = amenity.name

    # Add dynamically created fields to the serializers class
    amenity_fields = locals().copy()
    amenity_fields.pop('amenities')  # Remove the amenities queryset
    amenity_fields.pop('amenity')  # Remove the amenities model
    locals().update(amenity_fields)

    print(locals())

    def validate(self, data):
        # Check that start_date is before end_date.
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        if check_in >= check_out:
            raise serializers.ValidationError({'detail': "End date must be after start date"})
        if (data.get('starts_at') is None and data.get('ends_at') is not None
                or data.get('starts_at') is not None and data.get('ends_at') is None):
            raise serializers.ValidationError({'detail': "Provide both range values or go to play away."})

        return data


class AmenityParamDtoSerializer(DataclassSerializer):
    class Meta:
        dataclass = AmenityParamDto


class AmenityCategoryDtoSerializer(DataclassSerializer):
    amenities = AmenityParamDtoSerializer(many=True)

    class Meta:
        dataclass = AmenityCategoryDto
        fields = ['name', 'amenities']


class MyHotelItemSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    rating_avg = serializers.FloatField()
    # reviews_count = serializers.IntegerField()
    reservations_count = serializers.IntegerField()
    check_ins_count = serializers.IntegerField()
    cancellations_count = serializers.IntegerField()
    occupied_rooms_count = serializers.IntegerField()

    def get_address(self, obj):
        return f"{obj.address}, {obj.city.name}, {obj.city.country.name}"

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'stars', 'address', 'business_email', 'rating_avg',
                  'reservations_count', 'check_ins_count', 'cancellations_count', 'occupied_rooms_count']


class HotelInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    city_id = serializers.IntegerField()
    stars = serializers.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    about = serializers.CharField(max_length=350)
    staff_languages = serializers.ListField(child=serializers.IntegerField())
    website = serializers.URLField(default=None)
    business_email = serializers.CharField(default=None)
    country_code_id = serializers.IntegerField()
    contact_number = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    facilities = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class HotelRulesSerializer(serializers.Serializer):
    check_in_from = serializers.TimeField()
    check_in_until = serializers.TimeField()
    check_out_from = serializers.TimeField()
    check_out_until = serializers.TimeField()
    cancellation_policy = serializers.ChoiceField(choices=CancellationPolicy.choices)
    days_before_cancellation = serializers.IntegerField(default=0, validators=[MinValueValidator(1)])
    prepayment_policy = serializers.ChoiceField(choices=PrepaymentPolicy.choices)

    def validate(self, data):
        if data.get('check_in_until') < data.get('check_in_from'):
            raise serializers.ValidationError({'detail': 'check_in_until must be after check_in_from'})
        if data.get('check_out_until') < data.get('check_out_from'):
            raise serializers.ValidationError({'detail': 'check_out_until must be after check_out_from'})
        return data


class HotelParkingSituationSerializer(serializers.Serializer):
    parking_available = serializers.BooleanField()
    reservation_needed = serializers.BooleanField(required=False)
    parking_type = serializers.ChoiceField(choices=ParkingType.choices, required=False)

    def validate(self, data):
        print("parking data: ", data)
        parking_available = data.get('parking_available')
        reservation_needed = data.pop('reservation_needed', None)
        parking_type = data.pop('parking_type', None)
        print("parking type bro is:", parking_type, " , reservation_needed:", reservation_needed)
        if parking_available and reservation_needed is None or parking_type is None:
            raise serializers.ValidationError(
                {'detail': "If you set the parking to be available, then provide the other information"
                           " about it and don't be mad"})
        return data


class CreateHotelRequestSerializer(serializers.Serializer):
    hotel_info = HotelInfoSerializer()
    hotel_rules = HotelRulesSerializer()
    parking = HotelParkingSituationSerializer()


class CreateHotelFormSerializer(serializers.Serializer):
    body = serializers.JSONField()
    cover_img = serializers.ImageField()
    hotel_images = serializers.ListField(child=serializers.ImageField(), allow_empty=False)

    def validate(self, data):
        create_hotel_req = CreateHotelRequestSerializer(data=data.get('body'))
        if not create_hotel_req.is_valid():
            raise serializers.ValidationError(detail=create_hotel_req.errors)
        return data


class FilterReservationsParamsSerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    room_type = serializers.ChoiceField(choices=RoomTypeEnum.choices, default=None)
    status = serializers.ChoiceField(choices=ReservationStatus.choices, default=None)
    sort = serializers.ChoiceField(choices=SortReservations.choices, default=SortReservations.CHECK_IN.value)


class ReservationItemSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, reservation: Reservation):
        return f"{reservation.first_name} {reservation.last_name}"

    class Meta:
        model = Reservation
        fields = [
            'full_name', 'check_in', 'check_out', 'total_price', 'commission', 'status'
        ]


class EssentialHotelInfoSerializer(serializers.ModelSerializer):
    check_ins = serializers.IntegerField()
    check_outs = serializers.IntegerField()

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'check_ins', 'check_outs']


class EssentialReviewItemSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    def get_username(self, review: GuestReview):
        return f"{review.reservation.first_name} {review.reservation.last_name}"

    def get_profile_pic(self, review: GuestReview):
        return review.reservation.guest.profile_pic.url

    class Meta:
        model = GuestReview
        fields = ['id', 'username', 'profile_pic', 'title', 'rating', 'created_at']


class EssentialReservationInfoSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    def get_username(self, reservation: Reservation):
        return f"{reservation.first_name} {reservation.last_name}"

    def get_profile_pic(self, reservation: Reservation):
        return reservation.guest.profile_pic

    class Meta:
        model = Reservation
        fields = ['id', 'username', 'profile_pic', 'status', 'total_price']


class DailyIncomeSerializer(serializers.Serializer):
    date = serializers.DateField()
    income = serializers.IntegerField()


class OwnerDashboardSerializer(serializers.Serializer):
    hotels = EssentialHotelInfoSerializer(many=True)
    reviews = EssentialReviewItemSerializer(many=True)
    reservations = EssentialReservationInfoSerializer(many=True)
    daily_incomes = DailyIncomeSerializer(many=True)


# class HotelDashboardSerializer(serializers.Serializer):
#     reviews = EssentialReviewItemSerializer(many=True)
#     reservations = HotelDashboardReservationSerializer(many=True)
#     pass

class HotelDashboardInfoSerializer(DataclassSerializer):
    reviews = EssentialReviewItemSerializer(many=True)

    class Meta:
        dataclass = HotelDashboardInfoDto


class RoomTypeItemSerializer(serializers.ModelSerializer):
    categories = AmenityCategorySerializer(many=True)
    bed_types = BedTypeSerializer(many=True)
    rooms_count = serializers.IntegerField()
    occupied_rooms_count = serializers.IntegerField()

    class Meta:
        model = RoomType
        fields = ['id', 'name', 'rooms_count', 'occupied_rooms_count', 'bed_types', 'categories']
