from rest_framework import serializers as rest_serializers
from .models import PeriodicTour


class TourSerializer(rest_serializers.ModelSerializer):
    rating_avg = rest_serializers.IntegerField()
    reviews_count = rest_serializers.IntegerField()

    class Meta:
        model = PeriodicTour
        fields = ['id', 'title', 'description', 'price', 'cover_img', 'rating_avg', 'reviews_count']


class FilterToursRequestSerializer(rest_serializers.Serializer):
    check_in = rest_serializers.DateField()
    check_out = rest_serializers.DateField()


class TourDetailsSerializer(rest_serializers.ModelSerializer):
    number_of_reviews = rest_serializers.IntegerField()
    avg_ratings = rest_serializers.FloatField()

    class Meta:
        model = PeriodicTour
