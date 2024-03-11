from rest_framework import serializers as rest_serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework_dataclasses.serializers import DataclassSerializer

from apps.hotels.dtos import HotelDetailsDTO, ReviewDTO
from apps.hotels.models import Hotel, HotelImage, RoomType, GuestReview, Reservation, Amenity, AmenityCategory


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


class AmenityCategorySerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = AmenityCategory
        fields = '__all__'


class AmenitySerializer(rest_serializers.ModelSerializer):
    category = AmenityCategorySerializer()

    class Meta:
        model = Amenity
        fields = '__all__'


class HotelDetailsSerializer(DataclassSerializer):
    amenities = AmenitySerializer(many=True)

    class Meta:
        dataclass = HotelDetailsDTO
