from rest_framework import serializers as rest_serializers
from .models import PeriodicTour


class TourSerializer(rest_serializers.ModelSerializer):

    class Meta:
        model = PeriodicTour
        fields = ['id', 'title', 'description', 'price']
