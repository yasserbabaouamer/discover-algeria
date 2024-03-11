from django.db.models import Count, QuerySet, Avg, Min
from .dtos import *
from .converters import *
from apps.hotels.models import Hotel

hotel_dto_converter = HotelDetailsConverter()


def get_most_visited_hotels() -> QuerySet:
    return Hotel.objects.get_most_visited_hotels()


def get_hotel_details_by_id(hotel_id: int):
    hotel = Hotel.objects.get_hotel_by_id(hotel_id)
    if hotel is not None:
        hotel_dto = hotel_dto_converter.to_dto(hotel)
        return hotel_dto
    return None


def get_reviews_by_hotel_id(hotel_id):
    reviews = GuestReview.objects.get_reviews_by_hotel_id(hotel_id)
    if reviews is not None:
        review_converter = ReviewToDTOConverter()
        reviews_dtos = review_converter.to_dtos_list(reviews)
        return reviews_dtos
    return None
