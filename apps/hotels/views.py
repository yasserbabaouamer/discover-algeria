from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiRequest
from jsonschema.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services, serializers
from .permissions import IsOwner, IsGuest


class GetTopHotelsView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Get top hotels',
        responses={
            200: OpenApiResponse(response=serializers.HotelSerializer)
        }
    )
    def get(self, request):
        hotels = services.find_top_hotels()
        hotels_serializer = serializers.HotelSerializer(hotels, many=True)
        return Response(data=hotels_serializer.data, status=status.HTTP_200_OK)


class GetHotelDetailsView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Get Hotel details',
        responses=serializers.HotelDetailsSerializer,
    )
    def get(self, request, *args, **kwargs):
        hotel_id = kwargs.pop('hotel_id', None)
        if hotel_id is None:
            raise ValidationError({'detail': 'Provide a hotel id'})
        hotel = services.get_hotel_details_by_id(hotel_id)
        serialized_hotel = serializers.HotelDetailsSerializer(hotel)
        return Response(data=serialized_hotel.data, status=status.HTTP_200_OK)


class ListCreateHotelReviewView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Get Hotel Reviews',
        responses=serializers.ReviewDtoSerializer,
    )
    def get(self, request, *args, **kwargs):
        hotel_id = kwargs.pop('hotel_id', None)
        if hotel_id is None:
            raise ValidationError({'detail': 'Provide a hotel id'})
        hotel_reviews = services.get_reviews_by_hotel_id(hotel_id)
        serialized_reviews = serializers.ReviewDtoSerializer(instance=hotel_reviews, many=True)
        return Response(data=serialized_reviews.data, status=status.HTTP_200_OK)


class GetHotelAvailableRoomTypes(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Get The Room Types of a Specific Hotel',
        parameters=[serializers.GetHotelAvailableRoomTypesParamsSerializer],
        responses={200: serializers.RoomTypeDtoSerializer}
    )
    def get(self, request, *args, **kwargs):
        hotel_id = kwargs.pop('hotel_id', None)
        if hotel_id is None:
            raise ValidationError({'detail': 'Provide a hotel id'})
        request_params = serializers.GetHotelAvailableRoomTypesParamsSerializer(data=self.request.query_params)
        if not request_params.is_valid():
            raise ValidationError({'detail': 'Provide check_in & check_out params'})
        room_types = services.get_room_types_by_hotel_id(hotel_id, request_params.validated_data)
        response = serializers.RoomTypeDtoSerializer(room_types, many=True)
        return Response(data=response.data, status=status.HTTP_200_OK)


class CreateReservationView(APIView):
    permission_classes = [IsGuest]

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


class FindHotelsByCity(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Filter City Hotels',
        parameters=[serializers.FilterRequestSerializer],
        responses={
            200: serializers.HotelDetailsSerializer
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


class GetAllAmenities(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Hotels'],
        summary='Get all amenities',
        responses={
            200: OpenApiResponse(response=serializers.AmenityCategoryDtoSerializer)
        }
    )
    def get(self, request):
        response = serializers.AmenityCategoryDtoSerializer(services.find_hotel_amenities(), many=True)
        return Response(data=response.data, status=status.HTTP_200_OK)


# Owner Dashboard endpoints

class GetOwnerDashboardInfo(APIView):
    permission_classes = [IsOwner]

    def get(self, request, *args, **kwargs):
        dashboard_info = services.find_owner_dashboard_information(request.user.owner.id)
        pass


class ListCreateOwnerHotelView(APIView):
    permission_classes = [IsOwner]
    pagination_class = PageNumberPagination
    parser_classes = [JSONParser, MultiPartParser]

    @extend_schema(
        tags=['Owner Dashboard'],
        summary='Get List of Hotels - Owner',
        responses={
            200: serializers.MyHotelItemSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        page = kwargs.pop('page', 1)
        limit = kwargs.pop('limit', 10)
        hotels = services.find_hotels_by_owner(request.user.owner)
        response = serializers.MyHotelItemSerializer(hotels, many=True)
        return Response(data=response.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Create new hotel - Owner',
        request=serializers.CreateHotelFormSerializer,
        tags=['Owner Dashboard']
    )
    def post(self, _request, *args, **kwargs):
        create_hotel_form = serializers.CreateHotelFormSerializer(data=self.request.data)
        if not create_hotel_form.is_valid():
            raise ValidationError(create_hotel_form.errors)
        print('validated:', create_hotel_form.validated_data)
        services.create_new_hotel(self.request.user.owner, create_hotel_form.validated_data)
        return Response({'detail': 'Your hotel has been created successfully'}, status=status.HTTP_201_CREATED)


class GetHotelEditInformation(APIView):
    authentication_classes = []
    permission_classes = [IsOwner]

    @extend_schema(
        tags=['Owner Dashboard'],
        summary='Get Hotel information for edit',
        responses={
            200: OpenApiResponse(response=serializers.HotelEditInfoDtoSerializer)
        }
    )
    def get(self, request, *args, **kwargs):
        hotel_id = kwargs.pop('hotel_id', None)
        if hotel_id is None:
            raise ValidationError({'detail': 'Provide a hotel id'})
        self.check_object_permissions(request, services.find_hotel_by_id(hotel_id))
        hotel_edit_info = services.get_hotel_info_for_edit(hotel_id)
        response = serializers.HotelEditInfoDtoSerializer(hotel_edit_info)
        return Response(data=response.data, status=status.HTTP_200_OK)


class GetHotelCreateInformation(APIView):
    permission_classes = [IsOwner]

    def get(self, request, *args, **kwargs):
        create_hotel_info = services.get_essential_info_for_hotel_creation()
        response = serializers.HotelCreateInfoDtoSerializer(create_hotel_info)
        return Response(response.data)


class ManageOwnerHotelDetailsView(APIView):
    permission_classes = [IsOwner]
    parser_classes = [JSONParser, MultiPartParser]

    @extend_schema(
        summary='Get Hotel details aka Hotel Dashboard - Owner',
        tags=['Owner Dashboard'],
        responses=serializers.HotelDashboardInfoSerializer
    )
    def get(self, request, *args, **kwargs):
        hotel_id: int = kwargs.pop('hotel_id', None)
        if hotel_id is None:
            raise ValidationError({'detail': 'Provide the hotel id'})
        hotel = services.find_hotel_by_id(hotel_id)
        self.check_object_permissions(request, hotel)
        hotel_info = services.find_hotel_dashboard_details(hotel_id)
        response = serializers.HotelDashboardInfoSerializer(hotel_info)
        return Response(data=response.data, status=status.HTTP_200_OK)

    # TODO: Test this method later - it's working
    @extend_schema(
        summary='Update Hotel - Owner',
        tags=['Owner Dashboard'],
        request=[
            OpenApiRequest(request=serializers.UpdateHotelFormSerializer),
            OpenApiRequest(request=serializers.UpdateHotelRequestSerializer)
        ],
        responses={
            200: OpenApiResponse(description='Hotel updated successfully')
        }
    )
    def post(self, request, *args, **kwargs):
        hotel_id: int = kwargs.pop('hotel_id', None)
        if hotel_id is None:
            raise ValidationError({'detail': 'Provide the hotel id'})
        hotel = services.find_hotel_by_id(hotel_id)
        self.check_object_permissions(request, hotel)
        update_request = serializers.UpdateHotelFormSerializer(data=self.request.data)
        if not update_request.is_valid():
            raise ValidationError(update_request.errors)
        services.update_hotel(hotel_id, update_request.validated_data)
        return Response(data={'detail': "Your hotel has been updated successfully"},
                        status=status.HTTP_200_OK)

    @extend_schema(
        summary='Delete Hotel - Owner',
        tags=['Owner Dashboard'],
        responses={
            204: OpenApiResponse(description='Hotel has been deleted successfully')
        }
    )
    def delete(self, request, *args, **kwargs):
        hotel_id: int = kwargs.pop('hotel_id', None)
        if hotel_id is None:
            raise ValidationError({'detail': 'Provide the hotel id'})
        hotel = services.find_hotel_by_id(hotel_id)
        self.check_object_permissions(request, hotel)
        services.delete_owner_hotel(hotel_id)
        return Response(data={'detail': "Your hotel has been deleted"}, status=status.HTTP_204_NO_CONTENT)


class ListCreateOwnerReservationView(APIView):
    permission_classes = [IsOwner]

    @extend_schema(
        summary='Get My Reservations route',
        parameters=[serializers.FilterReservationsParamsSerializer],
        tags=['Owner Dashboard'],
        responses={
            200: OpenApiResponse(response=serializers.ReservationItemSerializer)
        }
    )
    def get(self, _request, *args, **kwargs):
        request = serializers.FilterReservationsParamsSerializer(data=self.request.query_params)
        if not request.is_valid():
            raise ValidationError(request.errors)
        hotel_id = kwargs.pop('hotel_id', None)
        if hotel_id is None:
            raise ValidationError({'detail': 'Provide the hotel id'})
        hotel = services.find_hotel_by_id(hotel_id)
        self.check_object_permissions(_request, hotel)
        reservations = services.find_reservations_by_hotel_id(hotel_id, request.validated_data)
        response = serializers.ReservationItemSerializer(reservations, many=True)
        return Response(response.data)


class ManageOwnerReservationView(APIView):
    permission_classes = [IsOwner]

    @extend_schema(
        summary='Cancel a reservation - Owner',
        tags=['Owner Dashboard'],
        responses={
            200: OpenApiResponse(description='Reservation has been canceled successfully')
        }
    )
    def put(self, request, *args, **kwargs):
        reservation_id = kwargs.pop('r_id', None)
        if reservation_id is None:
            raise ValidationError({'detail': "You have to provide a reservation_id"})
        hotel = services.find_hotel_by_reservation_id(reservation_id)
        self.check_object_permissions(request, hotel)
        services.cancel_reservation(reservation_id)
        return Response(data={'detail': "This Reservation has been cancelled"}, status=status.HTTP_200_OK)


class ListCreateRoomType(APIView):
    permission_classes = [IsOwner]

    @extend_schema(
        summary='Get Room types by hotel id - Owner',
        tags=['Owner Dashboard'],
        responses={
            200: OpenApiResponse(response=serializers.RoomTypeItemSerializer)
        }
    )
    def get(self, request, *args, **kwargs):
        hotel_id = kwargs.pop('hotel_id', None)
        if hotel_id is None:
            raise ValidationError({'detail': 'Provide a hotel id'})
        self.check_object_permissions(request, services.find_hotel_by_id(hotel_id))
        room_types = services.find_room_types_by_hotel_id(hotel_id)
        response = serializers.RoomTypeItemSerializer(room_types, many=True)
        return Response(response.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Create Room Type - Owner',
        tags=['Owner Dashboard'],
        request=serializers.CreateRoomTypeRequestSerializer,
        responses={
            100: OpenApiResponse(description="This is what you have to send",
                                 response=serializers.CreateRoomTypeFormSerializer),
            201: OpenApiResponse(description="Your room type has been created successfully")
        }
    )
    def post(self, request, *args, **kwargs):
        hotel_id = kwargs.pop('hotel_id', None)
        if hotel_id is None:
            raise ValidationError({'detail': 'Provide a hotel id'})
        self.check_object_permissions(request, services.find_hotel_by_id(hotel_id))
        create_room_type_form = serializers.CreateRoomTypeFormSerializer(data=request.data)
        if not create_room_type_form.is_valid():
            raise ValidationError(create_room_type_form.errors)
        services.create_room_type(hotel_id, create_room_type_form.validated_data)
        return Response({'detail': "Your room type has been created successfully"},
                        status=status.HTTP_201_CREATED)


class ManageHotelRoomType(APIView):
    permission_classes = [IsOwner]

    @extend_schema(
        summary='Get Room type by id - Owner',
        tags=['Owner Dashboard'],
        responses={
            200: OpenApiResponse()
        }
    )
    def get(self, request, *args, **kwargs):
        room_type_id = kwargs.pop('room_type_id', None)
        if room_type_id is None:
            raise ValidationError({'detail': 'Provide a room type id'})
        return Response()

    @extend_schema(
        summary='Update Room type',
        tags=['Owner Dashboard'],
        request=serializers.UpdateRoomTypeFormSerializer,
        responses={
            100: OpenApiResponse(description="This is what you have to send in the request"
                , response=serializers.UpdateRoomTypeRequestSerializer),
            200: OpenApiResponse(description='Successful update')
        }
    )
    def put(self, request, *args, **kwargs):
        room_type_id = kwargs.pop('room_type_id', None)
        if room_type_id is None:
            raise ValidationError({'detail': 'Provide a room type id'})
        hotel = services.find_hotel_by_room_type_id(room_type_id)
        self.check_object_permissions(request, hotel)
        update_room_type_form = serializers.UpdateRoomTypeFormSerializer(data=request.data)
        if not update_room_type_form.is_valid():
            raise ValidationError(update_room_type_form.errors)
        services.update_room_type(room_type_id, update_room_type_form.validated_data)
        return Response({'detail': 'The room type has been updated successfully'})

    @extend_schema(
        summary='Delete Room type',
        tags=['Owner Dashboard'],
        responses={
            200: OpenApiResponse(description="Room type deleted successfully")
        }
    )
    def delete(self, request, *args, **kwargs):
        room_type_id = kwargs.pop('room_type_id', None)
        if room_type_id is None:
            raise ValidationError({'detail': 'Provide a room type id'})
        room_type = services.find_room_type_by_id(room_type_id)
        self.check_object_permissions(request, room_type.hotel)
        services.delete_room_type(room_type_id)
        return Response({'detail': "The room type has been deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
