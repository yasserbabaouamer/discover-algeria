from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from . import services, serializers


# Create your views here.


class TopDestinationsView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Destinations'],
        summary='Get Top Destinations',
        responses={200: serializers.CitySerializer}
    )
    def get(self, request):
        cities = services.get_top_destinations()
        cities_serializer = serializers.CitySerializer(cities, many=True)
        return Response(data=cities_serializer.data, status=status.HTTP_200_OK)


class GetCityDetailsView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Destinations'],
        summary='Get city details',
        responses={
            200: OpenApiResponse(response=serializers.CityDetailsSerializer)
        }
    )
    def get(self, request):
        try:
            city_id = self.request.query_params['id']
            city = services.get_city_details_by_id(city_id)
            response = serializers.CityDetailsSerializer(city)
            return Response(data=response.data, status=status.HTTP_200_OK)
        except KeyError as e:
            raise ValidationError({'detail': 'Provide a city id'})


class CountryCodeView(ListAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = services.find_all_countries_codes()
    serializer_class = serializers.CountryCodeSerializer

    @extend_schema(
        tags=['Destinations'],
        summary='Get country codes'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
