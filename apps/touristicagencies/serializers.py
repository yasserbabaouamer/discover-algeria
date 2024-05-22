from rest_framework import serializers
from .models import PeriodicTour, TouristicAgency, TourImage
from ..destinations.serializers import CitySerializer


class TourSerializer(serializers.ModelSerializer):
    rating_avg = serializers.IntegerField()
    reviews_count = serializers.IntegerField()

    class Meta:
        model = PeriodicTour
        fields = ['id', 'title', 'description', 'price', 'cover_img', 'rating_avg', 'reviews_count']


class FilterToursRequestSerializer(serializers.Serializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()


class TourismAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristicAgency
        fields = ['id', 'name', 'cover_img']


class PeriodicTourImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourImage
        fields = ['id', 'image']


class TourDetailsSerializer(serializers.ModelSerializer):
    reviews_count = serializers.IntegerField()
    rating_avg = serializers.FloatField()
    city = CitySerializer()
    agency = TourismAgencySerializer(source='touristic_agency')
    images = PeriodicTourImageSerializer(many=True)

    class Meta:
        model = PeriodicTour
        fields = ['id', 'title', 'city', 'description', 'agency', 'price', 'reviews_count',
                  'rating_avg', 'cover_img', 'images']
