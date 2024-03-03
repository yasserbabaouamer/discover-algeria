import faker
from faker import Faker, Generator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from . import services, serializers


class GetMostVisitedHotelsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        hotels = services.get_most_visited_hotels()
        hotels_serializer = serializers.HotelSerializer(hotels, many=True)
        return Response(data=hotels_serializer.data, status=status.HTTP_200_OK)


class FillDb(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):

        return Response(status=status.HTTP_200_OK)
