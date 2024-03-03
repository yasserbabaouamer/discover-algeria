from rest_framework import serializers as rest_serializers
from . import models


class DestinationSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = ['id', 'name']
