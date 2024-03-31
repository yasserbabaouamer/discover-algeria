from .dtos import *
from .models import Hotel, GuestReview, RoomType, Room


class ReviewToDTOConverter:

    def to_dto(self, review: GuestReview) -> ReviewDTO:
        return ReviewDTO(
            review.id, review.title, review.content, review.created_at
        )

    def to_dtos_list(self, reviews) -> List[ReviewDTO]:
        return [self.to_dto(review) for review in reviews]


class HotelDetailsConverter:
    review_converter = ReviewToDTOConverter()

    def to_dto(self, hotel: Hotel) -> HotelDetailsDTO:
        return HotelDetailsDTO(
            hotel.id, hotel.name, hotel.stars, f"{hotel.address} , {hotel.city.name} , {hotel.city.country.name}",
            hotel.longitude, hotel.latitude, hotel.website_url, hotel.cover_img.path, hotel.about, hotel.business_email,
            hotel.contact_number, hotel.amenities.all()
        )


class RoomTypeConverter:

    def to_dto(self, room_type: RoomType, check_in=None, check_out=None) -> RoomTypeDTO:
        return RoomTypeDTO(
            room_type.id, room_type.name, room_type.size, room_type.nb_beds, room_type.main_bed_type,
            room_type.price_per_night,
            room_type.cover_img.path,
            Room.objects.get_available_rooms_by_room_type(room_type.id, check_in, check_out).count()
            if check_in is not None and check_out is not None else None,
            RoomType.objects.get_categories_and_amenities(room_type.id)
        )

    def to_dtos_list(self, room_types: List[RoomType]) -> List[RoomTypeDTO]:
        return [self.to_dto(room_type) for room_type in room_types]
