from typing import List

from django.db.models import QuerySet

from .models import Hotel, GuestReview, RoomType, Reservation
from .dtos import *


class ReviewToDTOConverter:

    def to_dto(self, review: GuestReview) -> ReviewDTO:
        return ReviewDTO(
            review.id, review.title, review.content, review.created_at
        )

    def to_dtos_list(self, reviews) -> List[ReviewDTO]:
        reviews_dtos = []
        for review in reviews:
            reviews_dtos.append(self.to_dto(review))
        return reviews_dtos


class HotelDetailsConverter:
    review_converter = ReviewToDTOConverter()

    def to_dto(self, hotel: Hotel) -> HotelDetailsDTO:
        return HotelDetailsDTO(
            hotel.id, hotel.name, hotel.stars, f"{hotel.address} , {hotel.city.name} , {hotel.city.country.name}",
            hotel.longitude, hotel.latitude, hotel.website_url, hotel.cover_img, hotel.about, hotel.business_email,
            hotel.contact_number, hotel.amenities.all()
        )
