from datetime import datetime as _datetime
from datetime import time

import stripe
from decouple import config
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction, connection
from django.db.models import QuerySet
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.hotels.models import Reservation, ReservedRoomType, RoomAssignment, HotelImage, ParkingSituation, \
    RoomTypeImage, BedType
from core.utils import CustomException
from .converters import *
from .enums import HotelStatus, ReservationStatus, RoomTypeStatus, HotelCancellationPolicy, RoomTypeEnum, \
    RoomTypeCancellationPolicy, RoomTypePrepaymentPolicy, RoomStatus
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
    hotel_dto = hotel_converter.to_dto(hotel)
    return hotel_dto


def get_room_types_by_hotel_id(hotel_id: int, dates: dict):
    room_types = RoomType.objects.find_available_room_types_by_hotel_id(hotel_id, dates['check_in'], dates['check_out'])
    room_types_dto = room_type_converter.to_dtos_list(room_types)
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
            return reservation.id


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
    stars = search_req.pop('stars', None)
    hotels = Hotel.objects.find_available_hotels_by_city_id(
        city_id=city_id,
        check_in=check_in,
        check_out=check_out,
        price_starts_at=price_starts_at,
        price_ends_at=price_ends_at,
        stars=stars,
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
    # Update the days before cancellation
    if hotel_rules['cancellation_policy'] != HotelCancellationPolicy.FIXED.value:
        hotel_rules['days_before_cancellation'] = 0
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


def find_room_type_by_id(room_type_id):
    return get_object_or_404(RoomType, pk=room_type_id)


def delete_room_type(room_type_id: int):
    room_type = RoomType.objects.find_by_id(room_type_id)
    room_type.status = RoomTypeStatus.DELETED_BY_OWNER.value
    room_type.save()


def update_hotel(request, hotel_id, form_data: dict):
    hotel_data: dict = form_data.get('body')
    hotel_info = hotel_data.get('hotel_info')
    hotel_rules = hotel_data.get('hotel_rules')
    parking = hotel_data.get('parking')
    parking_available = parking.pop('parking_available')
    added_staff_languages = get_list_or_404(Language, id__in=hotel_info.pop('added_staff_languages'))
    removed_staff_languages = get_list_or_404(Language, id__in=hotel_info.pop('removed_staff_languages'))
    added_amenities = get_list_or_404(Amenity, id__in=hotel_info.pop('added_facilities'))
    removed_amenities = get_list_or_404(Amenity, id__in=hotel_info.pop('removed_facilities'))
    print('removed images ids :', hotel_data['removed_images_ids'])
    removed_images = get_list_or_404(HotelImage, id__in=hotel_data['removed_images_ids'])
    print("images to remove: ", removed_images)
    added_images = form_data.get('added_images', [])
    cover_img = form_data.pop('cover_img', None)
    if cover_img is not None:
        hotel_info['cover_img'] = cover_img
    with transaction.atomic():
        hotel = Hotel.objects.find_with_rules_and_parking_and_images(hotel_id)
    print('Hotel attrs :', dir(hotel))
    # Update hotel information
    for key, value in hotel_info.items():
        setattr(hotel, key, value)
    hotel.parking_available = parking_available
    hotel.staff_languages.remove(*removed_staff_languages)
    hotel.staff_languages.add(*added_staff_languages)
    hotel.amenities.remove(*removed_amenities)
    hotel.amenities.add(*added_amenities)
    # Update hotel images
    hotel.images.remove(*removed_images)
    print("added images are:", added_images)
    for image in added_images:
        HotelImage.objects.create(hotel=hotel, img=image)
    # Update hotel rules
    for key, value in hotel_rules.items():
        setattr(hotel.rules, key, value)
    # Update hotel parking situation
    for key, value in parking.items():
        setattr(hotel.parking_situation, key, value)
    hotel.save()
    hotel.rules.save()
    hotel.parking_situation.save()


def create_room_type(hotel_id: int, form_data: dict):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    room_type_info = form_data.get('body')
    amenities = get_list_or_404(Amenity, id__in=room_type_info.get('amenities'))
    number_of_rooms: int = room_type_info.get('number_of_rooms')
    bed_type_quantities = room_type_info['bed_type_quantities']
    with transaction.atomic():
        # Add room type information
        room_type = RoomType.objects.create(
            hotel=hotel,
            name=room_type_info.get('type'),
            size=room_type_info.get('size'),
            price_per_night=room_type_info.get('price_per_night'),
            number_of_guests=room_type_info.get('number_of_guests'),
            cover_img=form_data.get('cover_img'),
        )
        room_type.amenities.add(*amenities)
        # Add room type images
        for image in form_data.get('images'):
            RoomTypeImage.objects.create(
                room_type=room_type,
                image=image
            )
        # Create rooms for this room type
        for i in range(number_of_rooms):
            Room.objects.create(
                room_type=room_type
            )
        # Add available bed types in this room type
        for bed_type_quantity in bed_type_quantities:
            if bed_type_quantity['quantity'] > 0:
                bed_type = get_object_or_404(BedType, pk=bed_type_quantity['bed_type_id'])
                RoomTypeBed.objects.create(
                    room_type=room_type,
                    bed_type=bed_type,
                    quantity=bed_type_quantity['quantity']
                )
        # Add policies
        RoomTypePolicies.objects.create(
            room_type=room_type,
            cancellation_policy=room_type_info['cancellation_policy'],
            days_before_cancellation=room_type_info.pop('days_before_cancellation', 0),
            prepayment_policy=room_type_info['prepayment_policy']
        )


def handle_updated_bed_type_quantities(room_type_id, new_bed_type_quantities: dict):
    # Fetch the original bed type quantities from the database
    old_bed_type_quantities = (RoomTypeBed.objects.filter(room_type_id=room_type_id)
                               .values_list('bed_type_id', 'quantity'))
    # Convert the original bed type quantities to a dictionary for easier comparison
    old_bed_type_quantities_dict = dict(old_bed_type_quantities)
    # Convert the new bed type quantities to a dictionary
    new_bed_type_quantities = {item['bed_type_id']: item['quantity'] for item in new_bed_type_quantities}
    print("new bed type quantities:", new_bed_type_quantities)
    # Identify added bed types (present in new list but not in original)
    added_bed_types = {bed_type_id: quantity for bed_type_id, quantity in new_bed_type_quantities.items() if
                       bed_type_id not in old_bed_type_quantities_dict and quantity != 0}
    print("added bed types:", added_bed_types)
    # Identify removed bed types (present in original list but not in new)
    removed_bed_types = {bed_type_id: quantity for bed_type_id, quantity in old_bed_type_quantities_dict.items()
                         if new_bed_type_quantities[bed_type_id] == 0}
    print("removed bed types:", removed_bed_types)
    # Identify updated bed types (present in both lists but with different quantities)
    updated_bed_types = {
        bed_type_id:
            {'old_quantity': old_bed_type_quantities_dict[bed_type_id], 'new_quantity': quantity} for
        bed_type_id, quantity in new_bed_type_quantities.items() if
        bed_type_id in old_bed_type_quantities_dict and old_bed_type_quantities_dict[bed_type_id] != quantity
        and quantity > 0
    }
    print("updated bed types:", updated_bed_types)
    return {
        'added_bed_types': added_bed_types,
        'updated_bed_types': updated_bed_types,
        'removed_bed_types': removed_bed_types,
    }


def update_room_type(room_type_id, form_data: dict):
    room_type = get_object_or_404(RoomType, pk=room_type_id)
    update_info: dict = form_data.get('body')
    added_images = form_data.get('added_images', [])
    removed_images_ids = update_info.get('removed_images', [])
    removed_images = get_list_or_404(RoomTypeImage, id__in=removed_images_ids)
    added_amenities = get_list_or_404(Amenity, id__in=update_info.get('added_amenities', []))
    removed_amenities = get_list_or_404(Amenity, id__in=update_info.get('removed_amenities', []))
    bed_type_quantities = update_info['bed_type_quantities']
    result = handle_updated_bed_type_quantities(room_type_id, bed_type_quantities)
    removed_bed_types = get_list_or_404(RoomTypeBed, bed_type_id__in=result['removed_bed_types'].keys())
    print('The pre removed bed types are :', removed_bed_types)
    with transaction.atomic():
        # Update room type information
        room_type.name = update_info['type']
        room_type.size = update_info.get('size')
        room_type.price_per_night = update_info['price_per_night']
        room_type.number_of_guests = update_info['number_of_guests']
        cover_img = form_data.pop('cover_img', None)
        if cover_img is not None:
            room_type.cover_img = cover_img
        room_type.amenities.remove(*removed_amenities)
        room_type.amenities.add(*added_amenities)

        # update rooms associated with that type
        old_rooms = Room.objects.filter(room_type=room_type, status=RoomStatus.VISIBLE)
        if old_rooms.count() > update_info['number_of_rooms']:
            count_of_deleted_rooms = old_rooms.count() - update_info['number_of_rooms']
            for i in range(count_of_deleted_rooms):
                room = get_object_or_404(Room, pk=old_rooms[i].id)
                room.status = RoomStatus.DELETED.value
                room.save()
        if old_rooms.count() < update_info['number_of_rooms']:
            count_of_added_rooms = update_info['number_of_rooms'] - old_rooms.count()
            for i in range(count_of_added_rooms):
                Room.objects.create(room_type=room_type)

        # Update room type images
        room_type.images.remove(*removed_images)
        for image in added_images:
            RoomTypeImage.objects.create(
                room_type=room_type,
                image=image
            )

        # Update room type beds
        for room_bed_type in removed_bed_types:
            room_bed_type.delete()
        for bed_type_id, quantity in result['added_bed_types'].items():
            RoomTypeBed.objects.create(
                room_type=room_type,
                bed_type_id=bed_type_id,
                quantity=quantity
            )
        for bed_type_id, quantities in result['updated_bed_types'].items():
            bed_type = get_object_or_404(RoomTypeBed, room_type=room_type, bed_type_id=bed_type_id)
            bed_type.quantity = quantities['new_quantity']
            bed_type.save()

        # Update room type policies
        room_type.policies.cancellation_policy = update_info['cancellation_policy']
        room_type.policies.days_before_cancellation = update_info.get('days_before_cancellation', 0)
        room_type.policies.prepayment_policy = update_info['prepayment_policy']
        room_type.policies.save()
        room_type.save()


def find_hotel_by_room_type_id(room_type_id):
    room_type = RoomType.objects.find_by_id(room_type_id)
    return room_type.hotel


def find_amenities_by_hotel_id(hotel_id):
    return Amenity.objects.find_amenities_by_hotel_id(hotel_id)


def get_hotel_info_for_edit(request, hotel_id) -> HotelEditInfoDTO:
    hotel = Hotel.objects.select_related('rules').get(id=hotel_id)
    selected_cancellation_policy = hotel.rules.cancellation_policy
    selected_prepayment_policy = hotel.rules.prepayment_policy
    selected_parking_type = hotel.parking_situation.parking_type
    current_site = get_current_site(request)
    domain = f"http://{current_site.domain}"
    return HotelEditInfoDTO(
        hotel.id, hotel.name, hotel.stars, hotel.address, hotel.longitude, hotel.latitude,
        hotel.website_url, domain + hotel.cover_img.url, hotel.about, hotel.business_email, hotel.contact_number,
        hotel.city.id, hotel.city.country.id, hotel.country_code.id,
        [CountryCodeDTO(country.id, country.name, country.country_code) for country in Country.objects.all()],
        [BaseCityDTO(city.id, city.name) for city in City.objects.all()],
        [AmenityDTO(facility.id, facility.name, domain + facility.icon.url, facility.checked)
         for facility in Amenity.objects.find_amenities_by_hotel_id(hotel.id)],
        [StaffLanguageDTO(language.id, language.name, language.checked)
         for language in Language.objects.find_languages_by_hotel_id(hotel_id)],
        hotel.rules.check_in_from, hotel.rules.check_in_until,
        hotel.rules.check_out_from, hotel.rules.check_out_until,
        [get_cancellation_policy_dto(policy, selected_cancellation_policy) for policy in
         HotelCancellationPolicy], hotel.rules.days_before_cancellation,
        [HotelPrepaymentPolicyDTO(policy, policy == selected_prepayment_policy)
         for policy in HotelPrepaymentPolicy],
        hotel.parking_available,
        hotel.parking_situation.reservation_needed,
        [ParkingTypeDTO(parking_type, parking_type == selected_parking_type)
         for parking_type in ParkingType],
        [ImageDTO(image.id, domain + image.img.url) for image in hotel.images.all()]
    )


def find_owner_dashboard_information(owner_id):
    review_converter = ReviewDtoConverter()
    hotels = Hotel.objects.find_owner_hotels(owner_id)[:10]
    latest_reservations = Reservation.objects.find_latest_reservations_to_owner_hotel(owner_id)
    latest_reviews = GuestReview.objects.find_latest_reviews_relate_to_owner(owner_id)
    return OwnerDashboardDTO(
        [EssentialHotelDTO(hotel.id, hotel.name, hotel.check_ins_count, hotel.reservations_count)
         for hotel in hotels],
        review_converter.to_dtos_list(latest_reviews),
        [ReservationDTO(reservation.id, f"{reservation.guest.first_name} {reservation.guest.last_name}",
                        reservation.guest.profile_pic.url, reservation.status, reservation.total_price)
         for reservation in latest_reservations],
        []
    )


def get_essential_info_for_hotel_creation():
    countries = Country.objects.all()
    cities = City.objects.all()
    languages = Language.objects.all()
    facilities = Amenity.objects.filter(category__name='Facilities').all()
    obj = HotelCreateInfoDTO(
        [CountryDTO(country.id, country.name, False) for country in countries],
        [CityDTO(city.id, city.name, False, city.country.id) for city in cities],
        [StaffLanguageDTO(language.id, language.name, False) for language in languages],
        [AmenityDTO(facility.id, facility.name, facility.icon.url, False) for facility in facilities],
        [HotelCancellationPolicyDTO(policy, False) for policy in HotelCancellationPolicy],
        [HotelPrepaymentPolicyDTO(policy, False) for policy in HotelPrepaymentPolicy],
        [ParkingTypeDTO(type, False) for type in ParkingType]
    )
    obj.cancellation_policies[0].checked = True
    obj.prepayment_policies[0].checked = True
    obj.parking_types[0].checked = True
    return obj


def get_essential_info_for_room_creation():
    return CreateRoomInfoDTO(
        [room for room in RoomTypeEnum],
        [AmenityDTO(amenity.id, amenity.name, amenity.icon.url, False) for amenity in
         Amenity.objects.find_all_rooms_amenities()],
        [RoomCancellationPolicyDTO(policy, False) for policy in RoomTypeCancellationPolicy],
        [RoomPrepaymentPolicyDTO(policy, False) for policy in RoomTypePrepaymentPolicy],
    )


def get_room_info_for_edit(request, room_type_id):
    room_type = RoomType.objects.find_by_id(room_type_id)
    selected_cancellation_policy = room_type.policies.cancellation_policy
    selected_prepayment_policy = room_type.policies.prepayment_policy
    current_site = get_current_site(request)
    domain = f"http://{current_site.domain}"
    return RoomEditInfoDTO(
        room_type.name, room_type.rooms_count, room_type.number_of_guests, room_type.price_per_night,
        room_type.size, [_type for _type in RoomTypeEnum],
        [AmenityDTO(amenity.id, amenity.name, domain + amenity.icon.url, amenity.checked)
         for amenity in Amenity.objects.find_amenities_by_room_type_id(room_type_id)],
        [RoomCancellationPolicyDTO(policy, policy == selected_cancellation_policy) for policy in
         RoomTypeCancellationPolicy], room_type.policies.days_before_cancellation,
        [RoomPrepaymentPolicyDTO(policy, policy == selected_prepayment_policy)
         for policy in RoomTypePrepaymentPolicy],
        BedType.objects.find_all_beds_for_room_type(room_type_id),
        domain + room_type.cover_img.url,
        [ImageDTO(image.id, domain + image.image.url) for image in room_type.images.all()]
    )


def convert_dzd_to_usd(dzd_price):
    conversion_rate = 150  # 1 USD = 150 DZD
    usd_price = dzd_price / conversion_rate
    return int(round(usd_price))


def create_payment_intent(data: dict):
    stripe.api_key = config('STRIPE_SECRET_KEY')
    reservation = get_object_or_404(Reservation, pk=data['reservation_id'])
    amount = convert_dzd_to_usd(reservation.total_price)
    payment_intent = stripe.PaymentIntent.create(
        amount=amount * 100,
        currency='usd',
        metadata={'reservation_id': data['reservation_id']},
        payment_method_types=['card'],
    )
    return payment_intent


def verify_payment_intent(data: dict):
    success, detail = True, "success"
    try:
        intent = stripe.PaymentIntent.retrieve(data['payment_intent_id'])
        print('intent status :', intent.status)
        if intent.status != 'succeeded':
            return False, 'Payment not successful'
        # Case of successful payment
        reservation = get_object_or_404(Reservation, pk=intent.metadata['reservation_id'])
        reservation.status = ReservationStatus.CONFIRMED
        reservation.save()
    except stripe.error.StripeError as e:
        return CustomException({'detail': e}, status=status.HTTP_406_NOT_ACCEPTABLE)
    return success, detail
