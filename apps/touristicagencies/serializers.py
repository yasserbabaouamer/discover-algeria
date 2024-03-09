from rest_framework import serializers as rest_serializers
from .models import Tour


class TourSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = ['id', 'title', 'description', 'price']
