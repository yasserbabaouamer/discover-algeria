from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from apps.hotels.models import Amenity
from apps.search.dtos import SearchItem


class GeneralSearchSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    number_of_adults = serializers.IntegerField(required=False)
    number_of_children = serializers.IntegerField(required=False)

    def validate(self, data):
        # Check that start_date is before end_date.
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({'detail': "End date must be after start date"})
        return data


class SearchItemSerializer(DataclassSerializer):
    class Meta:
        dataclass = SearchItem


class SearchByCitySerializer(serializers.Serializer):
    city_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    number_of_adults = serializers.IntegerField()
    number_of_children = serializers.IntegerField()

    def validate(self, data):
        # Check that start_date is before end_date.
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date")
        return data


