from datetime import datetime as _datetime
from datetime import time

from django.db import transaction, connection
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from apps.hotels.models import Hotel, Reservation, ReservedRoomType, RoomAssignment
from .converters import *
from .serializers import FilterRequestSerializer
from ..destinations.models import Country
from ..users.models import User

hotel_converter = HotelDetailsDtoConverter()
room_type_converter = RoomTypeConverter()


def get_most_visited_hotels() -> QuerySet:
    return Hotel.objects.get_most_visited_hotels()


def get_hotel_details_by_id(hotel_id: int):
    hotel = Hotel.objects.find_by_id(hotel_id)
    if hotel is not None:
        hotel_dto = hotel_converter.to_dto(hotel)
        return hotel_dto
    return None


def get_room_types_by_hotel_id(hotel_id: int):
    hotel = Hotel.objects.find_by_id(hotel_id)
    room_types_dto = room_type_converter.to_dtos_list(hotel.room_types.all())
    return room_types_dto


def get_reviews_by_hotel_id(hotel_id):
    reviews = GuestReview.objects.get_reviews_by_hotel_id(hotel_id)
    review_converter = ReviewToDTOConverter()
    reviews_dtos = review_converter.to_dtos_list(reviews)
    return reviews_dtos


def reserve_hotel_room(user: User, request: dict):
    # Check Hotel & Country Existence
    hotel = Hotel.objects.find_by_id(request['hotel_id'])
    country = Country.objects.find_by_id(request['country_id'])
    if user.guest:
        check_in = request['check_in']
        check_out = request['check_out']
        nb_nights = (check_out - check_in).days
        total_price = calculate_total_price(request['requested_room_types'], nb_nights)
        check_in = _datetime.combine(check_in, time(13, 0))
        check_out = _datetime.combine(check_out, time(12, 0))
        with transaction.atomic():
            cursor = connection.cursor()
            cursor.execute('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE')
            reservation = Reservation.objects.create_reservation(
                guest=user.guest,
                first_name=request['first_name'],
                last_name=request['last_name'],
                email=request['email'],
                country=country,
                phone=request['phone'],
                check_in=check_in,
                check_out=check_out,
                total_price=total_price,
                hotel=hotel
            )
            for item in request['requested_room_types']:
                rooms = Room.objects.get_available_rooms_by_room_type(item['room_type_id'], check_in, check_out)
                if rooms.count() < item['nb_rooms']:
                    raise ValidationError(
                        {'detail': f"Insufficient available rooms for room type {item['room_type_id']}"}
                    )
                reserved_room_type = ReservedRoomType.objects.create(
                    reservation=reservation,
                    room_type_id=item['room_type_id'],
                    nb_rooms=item['nb_rooms']
                )
                rooms_list = list(rooms)
                for i in range(item['nb_rooms']):
                    RoomAssignment.objects.create(
                        room=rooms_list[i],
                        reserved_room_type=reserved_room_type
                    )
    else:
        raise ValidationError({'detail': "You don't have a guest account , create one then try again."})


def calculate_total_price(requested_room_types, nb_nights) -> int:
    total_price = 0
    for item in requested_room_types:
        _id = item['room_type_id']
        price_per_night = RoomType.objects.find_by_id(_id).price_per_night
        total_price += total_price + price_per_night * item['nb_rooms'] * nb_nights
    return total_price


def filter_city_hotels(city_id, search_req: dict):
    check_in = _datetime.combine(search_req['check_in'], time(13, 0))
    check_out = _datetime.combine(search_req['check_out'], time(12, 0))
    hotels = Hotel.objects.find_available_hotels_by_city_id(city_id, check_in, check_out)
    print("Available Hotels :", hotels)
    search_req.pop('check_in')
    search_req.pop('check_out')
    search_req.pop('number_of_adults')
    search_req.pop('number_of_children')
    for hotel in hotels:
        for key, value in search_req.items():
            if value:
                if not Hotel.objects.has_amenity(hotel.id, FilterRequestSerializer.amenity_map[key]):
                    hotels.remove(hotel)
                    break

    converter = HotelDetailsDtoConverter()
    return converter.to_dtos_list(hotels)
