from rest_framework import serializers as rest_serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_dataclasses.serializers import DataclassSerializer

from . import models
from .dtos import CityDetailsDTO


class CitySerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = ['id', 'name', 'cover_img']


class CityImageSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = models.CityImage
        fields = '__all__'


class CityDetailsSerializer(DataclassSerializer):
    class Meta:
        dataclass = CityDetailsDTO


class CountryCodeSerializer(ModelSerializer):
    class Meta:
        model = models.Country
        fields = ['id', 'country_code', 'flag']
