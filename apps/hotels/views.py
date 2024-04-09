from drf_spectacular.utils import extend_schema, OpenApiResponse
from jsonschema.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services, serializers


class GetMostVisitedHotelsView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Get the most visited hotels',
        responses=serializers.HotelSerializer,
    )
    def get(self, request):
        hotels = services.get_most_visited_hotels()
        hotels_serializer = serializers.HotelSerializer(hotels, many=True)
        return Response(data=hotels_serializer.data, status=status.HTTP_200_OK)


class HotelView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Get Hotel details',
        responses=serializers.HotelDetailsSerializer,
    )
    def get(self, request, hotel_id):
        hotel = services.get_hotel_details_by_id(hotel_id)
        serialized_hotel = serializers.HotelDetailsSerializer(hotel)
        return Response(data=serialized_hotel.data, status=status.HTTP_200_OK)


class HotelReviewsView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Get Hotel Reviews',
        responses=serializers.ReviewDtoSerializer,
    )
    def get(self, request, hotel_id):
        hotel_reviews = services.get_reviews_by_hotel_id(hotel_id)
        serialized_reviews = serializers.ReviewDtoSerializer(instance=hotel_reviews, many=True)
        return Response(data=serialized_reviews.data, status=status.HTTP_200_OK)


class GetHotelRoomTypes(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Get The Room Types of a Specific Hotel',
        responses={200: serializers.RoomTypeDtoSerializer}
    )
    def get(self, request, hotel_id):
        room_types = services.get_room_types_by_hotel_id(hotel_id)
        print(room_types)
        response = serializers.RoomTypeDtoSerializer(room_types, many=True)
        return Response(data=response.data, status=status.HTTP_200_OK)


class RoomReservationView(APIView):
    @extend_schema(
        tags=['Hotels'],
        summary='Reserve a hotel room',
        request=serializers.RoomReservationRequestSerializer,
        responses={
            201: OpenApiResponse(description='Your reservation has been created successfully')
        }
    )
    def post(self, request):
        reservation_request = serializers.RoomReservationRequestSerializer(data=request.data)
        if reservation_request.is_valid():
            services.reserve_hotel_room(self.request.user, reservation_request.validated_data)
            return Response({'detail': "Your reservation has been created successfully"}, status.HTTP_201_CREATED)
        raise ValidationError(detail=reservation_request.errors)


class SearchHotelsByCity(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Filter City Hotels',
        request=serializers.RoomReservationRequestSerializer,
        responses={
            201: OpenApiResponse(description='Your reservation has been created successfully')
        }
    )
    def get(self, _request, *args, **kwargs):
        city_id = kwargs.pop('city_id', None)
        if city_id is None:
            raise ValidationError({'detail': 'City id is required'})
        request = serializers.FilterRequestSerializer(data=self.request.query_params.dict())
        if request.is_valid():
            print('Validated Data :', request.validated_data)
            search_results = services.filter_city_hotels(city_id, request.validated_data)
            response = serializers.HotelDetailsSerializer(search_results, many=True)
            return Response(data=response.data, status=status.HTTP_200_OK)
        raise ValidationError(request.errors)



class GetFilters(ListAPIView):
    authentication_classes = []
    permission_classes = []



class FillDb(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Testing']
    )
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
