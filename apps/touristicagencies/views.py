from drf_spectacular.utils import extend_schema, OpenApiResponse
from jsonschema.exceptions import ValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services, serializers


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
        tags=['Touristic Agencies'],
        summary='Get city tours - There is an error for now',
        parameters=[serializers.FilterToursRequestSerializer],
        responses={
            200: OpenApiResponse(response=serializers.TourSerializer)
        }
    )
    def get(self, request, *args, **kwargs):
        city_id = self.kwargs.pop('city_id', None)
        if city_id is None:
            raise ValidationError({'detail': 'city_id is required'})
        filter_request = serializers.FilterToursRequestSerializer(data=self.request.query_params)
        if not filter_request.is_valid():
            raise ValidationError({'detail': 'Invalid params, see docs for details'})
        tours = services.find_available_tours(city_id, filter_request.validated_data)
        return Response(data=serializers.TourSerializer(tours).data)


class GetTourDetails(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Touristic Agencies'],
        summary='Get tour details',
        responses={
            200: OpenApiResponse(response=serializers.TourDetailsSerializer),
            400: OpenApiResponse(description='Pass a tour id'),
            404: OpenApiResponse(description='This tour does not exist')
        }
    )
    def get(self, request, *args, **kwargs):
        tour_id = kwargs.pop('tour_id', None)
        if tour_id is None:
            raise ValidationError({'detail': 'Provide a tour_id'})
        tour = services.find_tour_by_id(tour_id)
        response = serializers.TourDetailsSerializer(tour)
        return Response(response.data)
