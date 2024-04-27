from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from .dtos import *
from .enums import Prepayment
from .models import Hotel, HotelImage, RoomType, Reservation, Amenity, AmenityCategory, BedType


class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['id', 'img']


class HotelSerializer(serializers.ModelSerializer):
    reservations_count = serializers.IntegerField()
    rating = serializers.FloatField()
    starts_at = serializers.IntegerField()
    average = serializers.FloatField()
    images = HotelImageSerializer(many=True)

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


class CreateHotelRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    city_id = serializers.IntegerField()
    stars = serializers.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    about = serializers.CharField(max_length=350)
    staff_languages = serializers.ListField(child=serializers.IntegerField())
    website = serializers.URLField(default=None)
    business_email = serializers.CharField(default=None)
    country_code_id = serializers.IntegerField()
    phone = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    facilities = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    check_in_from = serializers.TimeField()
    check_in_until = serializers.TimeField()
    check_out_from = serializers.TimeField()
    check_out_until = serializers.TimeField()
    prepayment_policy = serializers.ChoiceField(choices=Prepayment.choices)
    parking_available = serializers.BooleanField()
    reservation_needed = serializers.BooleanField()
    cover_img = serializers.ImageField()
    hotel_images = serializers.ListField(child=serializers.ImageField(), allow_empty=False)
