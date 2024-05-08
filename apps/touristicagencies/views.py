from drf_spectacular.utils import extend_schema
from jsonschema.exceptions import ValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services, serializers
from .models import PeriodicTour


class GetTopTours(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Touristic Agencies'],
        summary='Get top tours in Algeria',
        responses=serializers.TourSerializer
    )
    def get(self, request, *args, **kwargs):
        response = serializers.TourSerializer(services.get_top_tours(), many=True)
        return Response(response.data)


class GetCityTours(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary='Get city tours',
        parameters=[serializers.FilterToursRequestSerializer]
    )
    def get(self, request, *args, **kwargs):
        city_id = self.kwargs.pop('city_id', None)
        if city_id is None:
            raise ValidationError({'detail': 'city_id is required'})
        filter_request = serializers.FilterToursRequestSerializer(data=self.request.data)
        if not filter_request.is_valid():
            raise ValidationError({'detail': 'Invalid params , see docs for details'})
        tours = services.find_available_tours(city_id, filter_request.validated_data)
        return Response(data=serializers.TourSerializer(tours).data)
