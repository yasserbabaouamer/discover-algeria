import faker
from drf_spectacular.utils import extend_schema
from faker import Faker, Generator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from . import services, serializers
from .serializers import ReviewDtoSerializer


class GetMostVisitedHotelsView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses=serializers.HotelSerializer, summary='Get the most visited hotels')
    def get(self, request):
        hotels = services.get_most_visited_hotels()
        hotels_serializer = serializers.HotelSerializer(hotels, many=True)
        return Response(data=hotels_serializer.data, status=status.HTTP_200_OK)


class HotelAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, hotel_id):
        hotel = services.get_hotel_details_by_id(hotel_id)
        if hotel is not None:
            print(hotel)
            serialized_hotel = serializers.HotelDetailsSerializer(hotel)
            return Response(data=serialized_hotel.data, status=status.HTTP_200_OK)
        return Response(data={'msg': f"Hotel with id : {hotel_id} does not exist"},
                        status=status.HTTP_400_BAD_REQUEST)


class HotelReviewsAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, hotel_id):
        hotel_reviews = services.get_reviews_by_hotel_id(hotel_id)
        print(hotel_reviews)
        serialized_reviews = ReviewDtoSerializer(instance=hotel_reviews, many=True)
        return Response(data=serialized_reviews.data, status=status.HTTP_200_OK)


class FillDb(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(status=status.HTTP_200_OK)
