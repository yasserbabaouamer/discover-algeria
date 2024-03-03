from rest_framework import serializers as rest_serializers

from apps.hotels.models import Hotel, HotelImage


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
