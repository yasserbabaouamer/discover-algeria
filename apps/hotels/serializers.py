import datetime
from datetime import timedelta

from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from rest_framework import serializers as rest_serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework_dataclasses.serializers import DataclassSerializer

from apps.hotels.dtos import HotelDetailsDTO, ReviewDTO, RoomTypeDTO
from apps.hotels.models import Hotel, HotelImage, RoomType, GuestReview, Reservation, Amenity, AmenityCategory, BedType


class HotelImageSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['id', 'img']


class HotelSerializer(rest_serializers.ModelSerializer):
    reservations_count = rest_serializers.IntegerField()
    rating = rest_serializers.FloatField()
    starts_at = rest_serializers.IntegerField()
    images = HotelImageSerializer(many=True)

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'stars', 'cover_img', 'starts_at', 'reservations_count', 'rating', 'images']


class RoomTypeSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ['id', 'cover_img', 'name', 'size', 'main_bed_type', 'price_per_night', 'nb_beds', 'amenities']


class ReviewDtoSerializer(DataclassSerializer):
    class Meta:
        dataclass = ReviewDTO


class ReservationSerializer(rest_serializers.ModelSerializer):
    review = ReviewDtoSerializer()

    class Meta:
        model = Reservation
        fields = ['review']  # Add other fields as needed


class AmenitySerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'


class AmenityCategorySerializer(rest_serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True)

    class Meta:
        model = AmenityCategory
        fields = ['id', 'name', 'icon', 'amenities']


class HotelDetailsSerializer(DataclassSerializer):
    amenities = AmenitySerializer(many=True)

    class Meta:
        dataclass = HotelDetailsDTO


class RoomTypeRequestSerializer(rest_serializers.Serializer):
    room_type_id = rest_serializers.IntegerField()
    nb_rooms = rest_serializers.IntegerField(validators=[MinValueValidator(1)])


class RoomReservationRequestSerializer(rest_serializers.Serializer):
    first_name = rest_serializers.CharField(max_length=255)
    last_name = rest_serializers.CharField(max_length=255)
    email = rest_serializers.EmailField()
    country = rest_serializers.IntegerField(validators=[MinValueValidator(0)])
    phone = rest_serializers.IntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
    hotel_id = rest_serializers.IntegerField(validators=[MinValueValidator(0)])
    check_in = rest_serializers.DateField()
    check_out = rest_serializers.DateField()
    requested_room_types = RoomTypeRequestSerializer(many=True)

    def validate(self, data):
        # Check that start_date is before end_date.
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        if check_in >= check_out:
            raise rest_serializers.ValidationError({'detail': "End date must be after start date"})
        return data


class BedTypeSerializer(rest_serializers.ModelSerializer):
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


class GetHotelAvailableRoomTypesRequestSerializer(rest_serializers.Serializer):
    check_in = rest_serializers.DateField(required=False)
    check_out = rest_serializers.DateField(required=False)


class FilterRequestSerializer(rest_serializers.Serializer):
    check_in = rest_serializers.DateField()
    check_out = rest_serializers.DateField()
    number_of_adults = rest_serializers.IntegerField(required=False, default=2)
    number_of_children = rest_serializers.IntegerField(required=False, default=0)
    amenities = Amenity.objects.all()
    # Dynamically create serializer fields for each amenity
    amenity_map = {}
    for amenity in amenities:
        field_name = amenity.name.lower().replace(' ', '_')
        locals()[field_name] = rest_serializers.BooleanField(required=False, default=False)
        amenity_map[field_name] = amenity.name

    # Add dynamically created fields to the serializer class
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
            raise rest_serializers.ValidationError({'detail': "End date must be after start date"})
        return data
