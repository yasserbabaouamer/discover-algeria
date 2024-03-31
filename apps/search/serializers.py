from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from apps.search.dtos import SearchItem


class SearchSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

    def validate(self, data):
        """
        Check that start_date is before end_date.
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date")

        return data


class SearchItemSerializer(DataclassSerializer):
    class Meta:
        dataclass = SearchItem
