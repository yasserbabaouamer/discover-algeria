import sys
from datetime import datetime as _datetime
from datetime import time

from django.db import transaction, connection
from django.db.models import QuerySet
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.hotels.models import Hotel, Reservation, ReservedRoomType, RoomAssignment, Language, HotelImage, HotelRules, \
    ParkingSituation
from .converters import *
from .enums import HotelStatus, ReservationStatus
from .serializers import FilterRequestSerializer
from ..destinations.models import Country
from ..owners.models import Owner
from ..users.models import User

MAX_LONG = 9223372036854775807

hotel_converter = HotelDetailsDtoConverter()
room_type_converter = RoomTypeConverter()


def find_top_hotels() -> QuerySet:
    return Hotel.objects.find_top_hotels()


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
    review_converter = ReviewDtoConverter()
    reviews_dtos = review_converter.to_dtos_list(reviews)
    return reviews_dtos


def reserve_hotel_room(user: User, request: dict):
    # Validate Data
    hotel = Hotel.objects.find_by_id(request['hotel_id'])
    country = Country.objects.find_by_id(request['country_id'])
    country_code = Country.objects.find_by_id(request['country_code_id'])
    check_in = request['check_in']
    check_out = request['check_out']
    nb_nights = (check_out - check_in).days
    check_in = _datetime.combine(check_in, time(13, 0))
    check_out = _datetime.combine(check_out, time(12, 0))
    # Calculate Total Price
    total_price = calculate_total_price(request['requested_room_types'], nb_nights)
    with transaction.atomic():
        cursor = connection.cursor()
        cursor.execute('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE')
        reservation = Reservation.objects.create_reservation(
            guest=user.guest,
            first_name=request['first_name'],
            last_name=request['last_name'],
            email=request['email'],
            country=country,
            country_code=country_code,
            phone=request['phone'],
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            hotel=hotel
        )
        for item in request['requested_room_types']:
            # Check for room availability for the requested room type
            rooms = Room.objects.find_available_rooms_by_room_type(item['room_type_id'], check_in, check_out)
            if rooms.count() < item['nb_rooms']:
                raise ValidationError(
                    {'detail': f"Insufficient available rooms for room type {item['room_type_id']}"}
                )
            # Create records to hold the requested room type and the number of rooms
            reserved_room_type = ReservedRoomType.objects.create(
                reservation=reservation,
                room_type_id=item['room_type_id'],
                nb_rooms=item['nb_rooms']
            )
            # Assign a set of rooms to the requested room type
            rooms_list = list(rooms)
            for i in range(item['nb_rooms']):
                RoomAssignment.objects.create(
                    room=rooms_list[i],
                    reserved_room_type=reserved_room_type
                )


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
    price_starts_at = search_req.pop('starts_at', 0)
    price_ends_at = search_req.pop('ends_at', MAX_LONG)
    hotels = Hotel.objects.find_available_hotels_by_city_id(
        city_id=city_id,
        check_in=check_in,
        check_out=check_out,
        price_starts_at=price_starts_at,
        price_ends_at=price_ends_at
    )
    print("Available Hotels :", hotels)
    search_req.pop('check_in')
    search_req.pop('check_out')
    search_req.pop('number_of_adults')
    search_req.pop('number_of_children')
    # Iterate over amenities
    for hotel in hotels:
        for key, value in search_req.items():
            if value:
                if not Hotel.objects.has_amenity(hotel.id, FilterRequestSerializer.amenity_map[key]):
                    hotels.remove(hotel)
                    break

    converter = HotelDetailsDtoConverter()
    return converter.to_dtos_list(hotels)


def find_hotel_amenities():
    converter = AmenityCategoryDtoConverter()
    return converter.to_dtos_list(AmenityCategory.objects.all())


def find_hotels_by_owner(owner: Owner):
    return Hotel.objects.find_owner_hotels(owner)


def create_new_hotel(owner: Owner, data: dict):
    hotel_data: dict = data.get('body')
    hotel_info = hotel_data.get('hotel_info')
    hotel_rules = hotel_data.get('hotel_rules')
    parking = hotel_data.get('parking')
    parking_available = parking.pop('parking_available')
    staff_languages = get_list_or_404(Language, id__in=hotel_info.pop('staff_languages'))
    amenities = get_list_or_404(Amenity, id__in=hotel_info.pop('facilities'))
    with transaction.atomic():
        hotel = Hotel.objects.create(
            owner=owner,
            **hotel_info,
            cover_img=data['cover_img'],
            parking_available=parking_available
        )
        for image_url in data['hotel_images']:
            HotelImage.objects.create(hotel=hotel, img=image_url)
        hotel.staff_languages.add(*staff_languages)
        hotel.amenities.add(*amenities)
        hotel.save()
        _hotel_rules = HotelRules.objects.create(hotel=hotel, **hotel_rules)
        if parking_available:
            _parking_situation = ParkingSituation.objects.create(hotel=hotel, **parking)


def find_hotel_by_id(hotel_id) -> Hotel:
    return get_object_or_404(Hotel, pk=hotel_id)


def delete_owner_hotel(hotel_id):
    hotel = Hotel.objects.find_by_id(hotel_id)
    hotel.status = HotelStatus.DELETED_BY_OWNER.value
    hotel.save()


def find_reservations_by_hotel_id(hotel_id: int, filters: dict):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    return Reservation.objects.find_reservations_by_hotel_id(hotel, filters)


def find_hotel_by_reservation_id(reservation_id):
    return get_object_or_404(Reservation, pk=reservation_id).hotel


def cancel_reservation(reservation_id: int):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    reservation.status = ReservationStatus.CANCELLED_BY_OWNER.value
    reservation.save()


def find_hotel_dashboard_details(hotel_id) -> HotelDashboardInfoDto:
    converter = HotelDashboardInfoDtoConverter()
    hotel = Hotel.objects.find_hotel_details_for_dashboard(hotel_id)
    return converter.to_dto(hotel)


def find_room_types_by_hotel_id(hotel_id: int):
    return RoomType.objects.find_room_types_by_hotel_id(hotel_id)
