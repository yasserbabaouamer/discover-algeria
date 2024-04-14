from drf_spectacular.utils import extend_schema
from jsonschema.exceptions import ValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from . import services, serializers


class GetTopTours(ListAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = services.get_top_tours()
    serializer_class = serializers.TourSerializer

    @extend_schema(
        tags=['Touristic Agencies'],
        summary='Get top tours in Algeria',
        responses=serializers.TourSerializer
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GetCityTours(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        city_id = self.kwargs.pop('city_id', None)
        if city_id is None:
            raise ValidationError({'detail': 'city_id is required'})
        filter_request = serializers.FilterToursRequestSerializer(data=self.request.data)
        if not filter_request.is_valid():
            raise ValidationError({'detail': 'Invalid params , see docs for details'})
        tours = services.find_available_tours(city_id, filter_request.validated_data)
