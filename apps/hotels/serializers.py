from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from .dtos import *
from .enums import HotelPrepaymentPolicy, ParkingType, HotelCancellationPolicy, SortReservations, RoomTypeEnum, \
    ReservationStatus, RoomTypeCancellationPolicy, RoomTypePrepaymentPolicy
from .models import Hotel, HotelImage, RoomType, Reservation, Amenity, AmenityCategory, BedType, GuestReview, Language
from ..destinations.models import Country, City

MAX_LONG = 9223372036854775807


class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['id', 'img']


class BaseHotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'cover_img']


class HotelSerializer(serializers.ModelSerializer):
    reviews_count = serializers.IntegerField()
    rating_avg = serializers.FloatField()
    starts_at = serializers.IntegerField()
    average = serializers.FloatField()

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'stars', 'average',
                  'cover_img', 'starts_at', 'reviews_count', 'rating_avg']


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
    """
    Use the same serializer for
    """

    def get_fields(self):
        fields = super().get_fields()
        # Add 'checked' field dynamically if it's not already defined in Meta class
        if 'checked' not in fields and hasattr(self.Meta.model, 'checked'):
            fields['checked'] = serializers.BooleanField(source='checked', read_only=True)
        return fields

    class Meta:
        model = Amenity
        fields = '__all__'


class AmenityCategorySerializer(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True)

    class Meta:
        model = AmenityCategory
        fields = ['id', 'name', 'icon', 'amenities']


class HotelRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelRules
        fields = '__all__'


class HotelDetailsSerializer(DataclassSerializer):
    amenities = AmenitySerializer(many=True)
    rules = HotelRulesSerializer()

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


class RoomTypeBedSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    def get_name(self, room_type_bed: RoomTypeBed):
        return room_type_bed.bed_type.name

    def get_icon(self, room_type_bed: RoomTypeBed):
        return room_type_bed.bed_type.icon.url

    class Meta:
        model = RoomTypeBed
        fields = ['bed_type_id', 'name', 'quantity', 'icon']


class RoomTypePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomTypePolicies
        fields = '__all__'


class RoomTypeDtoSerializer(DataclassSerializer):
    beds = RoomTypeBedSerializer(many=True)
    policies = RoomTypePolicySerializer()

    class Meta:
        dataclass = RoomTypeDTO
        fields = ["id", "name", "size", "price_per_night", "cover_img", "number_of_guests",
                  "available_rooms_count", "beds", "categories", "policies"]


class GetHotelAvailableRoomTypesParamsSerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()


class FilterRequestSerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    number_of_adults = serializers.IntegerField(required=False, default=2)
    number_of_children = serializers.IntegerField(required=False, default=0)
    starts_at = serializers.IntegerField(required=False, default=0)
    ends_at = serializers.IntegerField(required=False, default=MAX_LONG)
    stars = serializers.IntegerField(required=False, default=None,
                                     validators=[MinValueValidator(1), MaxValueValidator(5)])
    amenities = Amenity.objects.all()
    # Dynamically create serializers fields for each amenity
    amenity_map = {}
    for amenity in amenities:
        field_name = amenity.name.lower().replace(' ', '_')
        locals()[field_name] = serializers.BooleanField(required=False, default=False)
        amenity_map[field_name] = amenity.id

    # Add dynamically created fields to the serializers class
    amenity_fields = locals().copy()
    amenity_fields.pop('amenities')  # Remove the amenities queryset
    locals().update(amenity_fields)

    def validate(self, data):
        # Check that start_date is before end_date.
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        if check_in >= check_out:
            raise serializers.ValidationError({'detail': "End date must be after start date"})
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
    reviews_count = serializers.IntegerField()
    reservations_count = serializers.IntegerField()
    check_ins_count = serializers.IntegerField()
    cancellations_count = serializers.IntegerField()
    revenue = serializers.IntegerField()
    rooms_count = serializers.IntegerField()
    occupied_rooms_count = serializers.IntegerField()
    amenities = AmenitySerializer(many=True)

    def get_address(self, obj):
        return f"{obj.address}, {obj.city.name}, {obj.city.country.name}"

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'stars', 'address', 'business_email', 'rating_avg', 'reviews_count',
                  "cover_img", 'website_url', 'reservations_count', "revenue", 'check_ins_count',
                  'cancellations_count', 'rooms_count', 'occupied_rooms_count', 'amenities']


class BaseHotelInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    stars = serializers.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    about = serializers.CharField(max_length=350)
    business_email = serializers.CharField(default=None, allow_null=True)
    contact_number = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    website = serializers.URLField(default=None, allow_null=True)


class CreateHotelInfoSerializer(BaseHotelInfoSerializer):
    country_code_id = serializers.IntegerField()  # Phone number country code
    city_id = serializers.IntegerField()  # Current city id
    staff_languages = serializers.ListField(child=serializers.IntegerField())
    facilities = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class BaseHotelRulesSerializer(serializers.Serializer):
    check_in_from = serializers.TimeField()
    check_in_until = serializers.TimeField()
    check_out_from = serializers.TimeField()
    check_out_until = serializers.TimeField()
    days_before_cancellation = serializers.IntegerField(default=0, validators=[MinValueValidator(1)])


class CreateHotelRulesSerializer(BaseHotelRulesSerializer):
    cancellation_policy = serializers.ChoiceField(choices=HotelCancellationPolicy.choices)
    prepayment_policy = serializers.ChoiceField(choices=HotelPrepaymentPolicy.choices)

    def validate(self, data):
        if data.get('check_in_until') < data.get('check_in_from'):
            raise serializers.ValidationError({'detail': 'check_in_until must be after check_in_from'})
        if data.get('check_out_until') < data.get('check_out_from'):
            raise serializers.ValidationError({'detail': 'check_out_until must be after check_out_from'})
        return data


class BaseHotelParkingSituationSerializer(serializers.Serializer):
    parking_available = serializers.BooleanField()
    reservation_needed = serializers.BooleanField(required=False)


class CreateHotelParkingSituationSerializer(BaseHotelParkingSituationSerializer):
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
    hotel_info = CreateHotelInfoSerializer()
    hotel_rules = CreateHotelRulesSerializer()
    parking = CreateHotelParkingSituationSerializer()


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
    hotel_id = serializers.IntegerField(required=False)
    room_type = serializers.ChoiceField(choices=RoomTypeEnum.choices, required=False)
    status = serializers.ChoiceField(choices=ReservationStatus.choices, required=False)
    sort = serializers.ChoiceField(choices=SortReservations.choices, default=SortReservations.CHECK_IN.value)


class ReservationItemSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    hotel = BaseHotelSerializer()

    def get_full_name(self, reservation: Reservation):
        return f"{reservation.first_name} {reservation.last_name}"

    class Meta:
        model = Reservation
        fields = [
            'id', 'full_name', 'check_in', 'check_out', 'total_price', 'commission', 'status', 'hotel'
        ]


class EssentialHotelInfoSerializer(serializers.ModelSerializer):
    check_ins = serializers.IntegerField()

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'check_ins']


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


class OwnerDashboardSerializer(DataclassSerializer):
    # hotels = EssentialHotelInfoSerializer(many=True)
    # reviews = EssentialReviewItemSerializer(many=True)
    # reservations = EssentialReservationInfoSerializer(many=True)
    # daily_incomes = DailyIncomeSerializer(many=True)

    class Meta:
        dataclass = OwnerDashboardDTO


class HotelDashboardInfoSerializer(DataclassSerializer):
    reviews = EssentialReviewItemSerializer(many=True)

    class Meta:
        dataclass = HotelDashboardInfoDto


class RoomTypeItemSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    beds = RoomTypeBedSerializer(many=True)
    rooms_count = serializers.IntegerField()
    occupied_rooms_count = serializers.IntegerField()

    def get_categories(self, room_type):
        amenities = room_type.amenities.all()
        # Retrieve the categories of those amenities and their associated amenities
        categories_dict = {}
        for amenity in amenities:
            print('amenity:', amenity.name)
            category = amenity.category
            if category not in categories_dict.keys():
                categories_dict[category] = []
            categories_dict[category].append(amenity)
        result = []
        for category, amenities in categories_dict.items():
            result.append({'id': category.id, 'name': category.name,
                           'amenities': [
                               {'id': amenity.id, 'name': amenity.name}
                               for amenity in amenities
                           ]})
        return result

    class Meta:
        model = RoomType
        fields = ['id', 'name', 'cover_img', 'price_per_night',
                  'rooms_count', 'occupied_rooms_count', 'beds', 'categories']


# Update Hotel Serializers
class CountryCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    city_name = serializers.SerializerMethodField()

    def get_city_name(self, city):
        return f"{city.name}, {city.country.name}"

    def get_fields(self):
        fields = super().get_fields()
        # Add 'checked' field dynamically if it's not already defined in Meta class
        if 'checked' not in fields and hasattr(self.Meta.model, 'checked'):
            fields['checked'] = serializers.BooleanField(source='checked', read_only=True)
        return fields

    class Meta:
        model = City
        fields = ['id', 'city_name']


class StaffLanguageSerializer(serializers.ModelSerializer):

    def get_fields(self):
        fields = super().get_fields()
        # Add 'checked' field dynamically if it's not already defined in Meta class
        if 'checked' not in fields and hasattr(self.Meta.model, 'checked'):
            fields['checked'] = serializers.BooleanField(source='checked', read_only=True)
        return fields

    class Meta:
        model = Language
        fields = '__all__'


class HotelInfoSerializer(BaseHotelInfoSerializer):
    country_codes = CountryCodeSerializer(many=True)
    cities = CitySerializer(many=True)
    facilities = AmenitySerializer(many=True)
    staff_languages = StaffLanguageSerializer(many=True)


class HotelCancellationPolicySerializer(serializers.Serializer):
    policy = serializers.ChoiceField(choices=HotelCancellationPolicy.choices)
    checked = serializers.BooleanField()


class HotelPrepaymentPolicySerializer(serializers.Serializer):
    policy = serializers.ChoiceField(choices=HotelPrepaymentPolicy.choices)
    checked = serializers.BooleanField()


class ParkingTypeSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=ParkingType.choices)
    checked = serializers.BooleanField()


class HotelParkingSituationSerializer(BaseHotelParkingSituationSerializer):
    parking_types = ParkingTypeSerializer(many=True)


class AllHotelRulesSerializer(BaseHotelRulesSerializer):
    cancellation_policies = HotelCancellationPolicySerializer(many=True)
    prepayment_policies = HotelPrepaymentPolicySerializer(many=True)


class GetHotelInfoForUpdateSerializer(serializers.Serializer):
    hotel_info = HotelInfoSerializer()
    hotel_rules = AllHotelRulesSerializer()
    parking = HotelParkingSituationSerializer()


class UpdateHotelInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    city_id = serializers.IntegerField()
    stars = serializers.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    about = serializers.CharField(max_length=350)
    added_staff_languages = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    removed_staff_languages = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    website = serializers.URLField(default=None)
    business_email = serializers.CharField(default=None)
    country_code_id = serializers.IntegerField()
    contact_number = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    added_facilities = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    removed_facilities = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)


class UpdateHotelRequestSerializer(serializers.Serializer):
    hotel_info = UpdateHotelInfoSerializer()
    hotel_rules = CreateHotelRulesSerializer()
    parking = CreateHotelParkingSituationSerializer()
    removed_images_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)


class UpdateHotelFormSerializer(serializers.Serializer):
    body = serializers.JSONField()
    cover_img = serializers.ImageField(required=False)
    added_images = serializers.ListField(child=serializers.ImageField(), required=False)

    def validate(self, data):
        update_hotel_req = UpdateHotelRequestSerializer(data=data.get('body'))
        if not update_hotel_req.is_valid():
            raise serializers.ValidationError(detail=update_hotel_req.errors)
        print('validated data of update hotel request :', update_hotel_req.validated_data)
        return data


# Create Room Type Serializers

class BedTypeQuantitySerializer(serializers.Serializer):
    bed_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField(validators=[MinValueValidator(0)])

    def validate(self, data):
        # Check bed type existence
        bed_type = get_object_or_404(BedType, pk=data.get('bed_type_id'))
        return data


class CreateRoomTypeRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=RoomTypeEnum.choices)
    number_of_rooms = serializers.IntegerField(required=True, validators=[MinValueValidator(1)])
    number_of_guests = serializers.IntegerField(validators=[MinValueValidator(1)])
    bed_type_quantities = serializers.ListField(child=BedTypeQuantitySerializer(), allow_empty=False)
    size = serializers.IntegerField(validators=[MinValueValidator(1)])
    price_per_night = serializers.IntegerField(validators=[MinValueValidator(500)])
    amenities = serializers.ListField(child=serializers.IntegerField())
    cancellation_policy = serializers.ChoiceField(choices=RoomTypeCancellationPolicy.choices)
    days_before_cancellation = serializers.IntegerField(required=False, validators=[MinValueValidator(0)])
    prepayment_policy = serializers.ChoiceField(choices=RoomTypePrepaymentPolicy.choices)

    def validate(self, data):
        cancellation_policy = data.get('cancellation_policy')
        days_before_cancellation = data.pop('days_before_cancellation', None)
        if cancellation_policy == RoomTypeCancellationPolicy.BEFORE.value and days_before_cancellation is None:
            raise serializers.ValidationError(
                {'detail': "Set the number of days before cancellation"})
        return data


class CreateRoomTypeFormSerializer(serializers.Serializer):
    body = serializers.JSONField()
    cover_img = serializers.ImageField()
    images = serializers.ListField(child=serializers.ImageField(), allow_empty=True)

    def validate(self, data):
        body_data = data.get('body')
        print(body_data)
        create_room_type_request = CreateRoomTypeRequestSerializer(data=body_data)
        if not create_room_type_request.is_valid():
            raise serializers.ValidationError(detail=create_room_type_request.errors)
        print('validated data of create room request:', create_room_type_request.validated_data)
        return data


# Update Room Type Serializers

class UpdateRoomTypeRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=RoomTypeEnum.choices)
    number_of_rooms = serializers.IntegerField(validators=[MinValueValidator(1)], required=True)
    number_of_guests = serializers.IntegerField(validators=[MinValueValidator(1)])
    bed_type_quantities = serializers.ListField(child=BedTypeQuantitySerializer(), allow_empty=False)
    size = serializers.FloatField(validators=[MinValueValidator(1)])
    price_per_night = serializers.IntegerField(validators=[MinValueValidator(500)])
    added_amenities = serializers.ListField(child=serializers.IntegerField(), required=False)
    removed_amenities = serializers.ListField(child=serializers.IntegerField(), required=False)
    removed_images = serializers.ListField(child=serializers.IntegerField(), required=False)
    cancellation_policy = serializers.ChoiceField(choices=RoomTypeCancellationPolicy.choices)
    prepayment_policy = serializers.ChoiceField(choices=RoomTypePrepaymentPolicy.choices)

    def validate(self, data):
        # Get all available bed type IDs from the database
        available_bed_type_ids = set(BedType.objects.values_list('id', flat=True))
        print("available_bed_type_ids :", available_bed_type_ids)
        # Extract bed type IDs from the request data
        bed_type_ids_from_request = set(item['bed_type_id'] for item in data.get('bed_type_quantities'))
        print("bed type IDs from request :", bed_type_ids_from_request)
        # Check if all bed type IDs from the request are present in the available bed types
        if not bed_type_ids_from_request.issuperset(available_bed_type_ids):
            raise serializers.ValidationError("Not all bed types are specified in the request.")
        return data


class UpdateRoomTypeFormSerializer(serializers.Serializer):
    body = serializers.JSONField()
    cover_img = serializers.ImageField(required=False)
    added_images = serializers.ListField(child=serializers.ImageField(), required=False)

    def validate(self, data):
        print('data which comes :', data.get('body'))
        update_request = UpdateRoomTypeRequestSerializer(data=data.get('body'))
        if not update_request.is_valid():
            raise serializers.ValidationError(update_request.errors)
        print('validated data :', update_request.validated_data)
        return data


class HotelEditInfoDtoSerializer(DataclassSerializer):
    class Meta:
        dataclass = HotelEditInfoDTO


class HotelEditInfoSerializer(serializers.ModelSerializer):
    current_city_id = serializers.IntegerField()
    current_country_id = serializers.IntegerField()
    current_country_code_id = serializers.IntegerField()
    country_codes = serializers.ListField(child=serializers.DictField())
    cities = serializers.ListField(child=serializers.DictField())
    facilities = serializers.ListField(child=serializers.DictField())
    staff_languages = serializers.ListField(child=serializers.DictField())
    check_in_from = serializers.DateTimeField()
    check_in_until = serializers.DateTimeField()
    check_out_from = serializers.DateTimeField()
    check_out_until = serializers.DateTimeField()
    cancellation_policies = serializers.ListField(child=serializers.DictField())
    days_before_cancellation = serializers.IntegerField()
    prepayment_policies = serializers.ListField(child=serializers.DictField())
    parking_available = serializers.BooleanField()
    reservation_needed = serializers.BooleanField()
    parking_types = serializers.ListField(child=serializers.DictField())
    images = serializers.ListField(child=serializers.CharField())

    def get_current_city_id(self, obj):
        return obj.city.id

    def get_current_country_id(self, obj):
        return obj.city.country.id

    def get_current_country_code_id(self, obj):
        return obj.country_code.id

    def get_country_codes(self, obj):
        return obj

    def get_cities(self, obj):
        # Logic to get display value for cities
        pass

    def get_facilities(self, obj):
        # Logic to get display value for facilities
        pass

    def get_staff_languages(self, obj):
        # Logic to get display value for staff languages
        pass

    def get_check_in_from(self, obj):
        # Logic to get display value for check-in from datetime
        pass

    def get_check_in_until(self, obj):
        # Logic to get display value for check-in until datetime
        pass

    def get_check_out_from(self, obj):
        # Logic to get display value for check-out from datetime
        pass

    def get_check_out_until(self, obj):
        # Logic to get display value for check-out until datetime
        pass

    def get_cancellation_policies(self, obj):
        # Logic to get display value for cancellation policies
        pass

    def get_days_before_cancellation(self, obj):
        # Logic to get display value for days before cancellation
        pass

    def get_prepayment_policies(self, obj):
        # Logic to get display value for prepayment policies
        pass

    def get_parking_available(self, obj):
        # Logic to get display value for parking availability
        pass

    def get_reservation_needed(self, obj):
        # Logic to get display value for reservation needed
        pass

    def get_parking_types(self, obj):
        # Logic to get display value for parking types
        pass

    def get_images(self, obj):
        # Logic to get display value for images
        pass

    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'stars', 'address', 'longitude', 'latitude', 'website_url',
            'cover_img', 'about', 'business_email', 'contact_number', 'current_city_id',
            'current_country_id', 'current_country_code_id', 'country_codes', 'cities',
            'facilities', 'staff_languages', 'check_in_from', 'check_in_until',
            'check_out_from', 'check_out_until', 'cancellation_policies',
            'days_before_cancellation', 'prepayment_policies', 'parking_available',
            'reservation_needed', 'parking_types', 'images'
        ]


class HotelCreateInfoDtoSerializer(DataclassSerializer):
    class Meta:
        dataclass = HotelCreateInfoDTO


class CreateRoomInfoDtoSerializer(DataclassSerializer):
    class Meta:
        dataclass = CreateRoomInfoDTO


class BedTypeWithDefaultsSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()
    bed_type_id = serializers.IntegerField(source='id')

    class Meta:
        model = BedType
        fields = ['bed_type_id', 'name', 'icon', 'length', 'width', 'quantity']


class RoomEditInfoDtoSerializer(DataclassSerializer):
    beds = BedTypeWithDefaultsSerializer(many=True)

    class Meta:
        dataclass = RoomEditInfoDTO


class PaymentRequestSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()


class VerifyPaymentRequestSerializer(serializers.Serializer):
    payment_intent_id = serializers.CharField(max_length=255)
