from .dtos import *
from .models import Hotel, GuestReview, RoomType, Room


class ReviewDtoConverter:

    def to_dto(self, review: GuestReview) -> ReviewDTO:
        return ReviewDTO(
            review.id, review.title, review.content, review.rating, review.created_at
        )

    def to_dtos_list(self, reviews) -> List[ReviewDTO]:
        return [self.to_dto(review) for review in reviews]


class HotelDetailsDtoConverter:
    review_converter = ReviewDtoConverter()

    def to_dto(self, hotel: Hotel) -> HotelDetailsDTO:
        return HotelDetailsDTO(
            hotel.id, hotel.name, hotel.stars, f"{hotel.address} , {hotel.city.name} , {hotel.city.country.name}",
            hotel.starts_at, hotel.reviews_count, hotel.rating_avg, hotel.longitude, hotel.latitude,
            hotel.website_url, hotel.cover_img.url, hotel.about, hotel.business_email,
            hotel.contact_number, hotel.amenities.all()
        )

    def to_dtos_list(self, hotels) -> List[HotelDetailsDTO]:
        return [self.to_dto(hotel) for hotel in hotels]


class RoomTypeConverter:

    def to_dto(self, room_type: RoomType, check_in=None, check_out=None) -> RoomTypeDTO:
        return RoomTypeDTO(
            room_type.id, room_type.name, room_type.size, room_type.nb_beds, room_type.main_bed_type,
            room_type.price_per_night,
            room_type.cover_img.path,
            Room.objects.find_available_rooms_by_room_type(room_type.id, check_in, check_out).count()
            if check_in is not None and check_out is not None else None,
            RoomType.objects.get_categories_and_amenities(room_type.id)
        )

    def to_dtos_list(self, room_types: List[RoomType]) -> List[RoomTypeDTO]:
        return [self.to_dto(room_type) for room_type in room_types]


class AmenityParamDtoConverter:
    def to_dto(self, amenity: Amenity) -> AmenityParamDto:
        return AmenityParamDto(
            amenity.name, amenity.name.lower().replace(' ', '_')
        )

    def to_dtos_list(self, amenities):
        return [self.to_dto(amenity) for amenity in amenities]


class AmenityCategoryDtoConverter:
    converter = AmenityParamDtoConverter()

    def to_dto(self, category: AmenityCategory) -> AmenityCategoryDto:
        return AmenityCategoryDto(
            category.name, self.converter.to_dtos_list(category.amenities.all())
        )

    def to_dtos_list(self, categories) -> List[AmenityCategoryDto]:
        return [self.to_dto(c) for c in categories]


class HotelDashboardRoomTypeDtoConverter:
    def to_dto(self, room_type: RoomType) -> HotelDashboardRoomTypeDto:
        print(f"Monthly revenue for room_type {room_type.name} is : f{room_type.monthly_revenue}")
        return HotelDashboardRoomTypeDto(
            room_type.id, room_type.rooms_count, room_type.occupied_rooms_count, room_type.monthly_revenue
        )

    def to_dtos_list(self, room_types):
        return [self.to_dto(room_type) for room_type in room_types]


class HotelDashboardInfoDtoConverter:
    room_type_converter = HotelDashboardRoomTypeDtoConverter()

    def to_dto(self, hotel: Hotel) -> HotelDashboardInfoDto:
        return HotelDashboardInfoDto(
            hotel.id, hotel.name, hotel.stars,
            f"{hotel.address}, {hotel.city.name}, {hotel.city.country.name}",
            hotel.longitude, hotel.latitude, hotel.rating_avg, HotelDashboardReservationDto(
                hotel.completed_count, hotel.cancellations_count, hotel.revenue
            ), self.room_type_converter.to_dtos_list(hotel.room_types.all()),
            [r.review for r in hotel.reservations.all()]
        )

    # class HotelItemDtoConverter:
    #     amenity_converter = Amenity
    #
    #     def to_dto(self, hotel: Hotel) -> HotelItemDto:
    #         return HotelItemDto(
    #             hotel.id, hotel.name, hotel.stars, f"{hotel.address}, {hotel.city.name}, {hotel.city.country.name}",
    #             hotel.website_url, hotel.business_email, hotel.nb_rooms, hotel.nb_occupied_rooms, hotel.nb_reservations,
    #             hotel.nb_check_ins, hotel.nb_cancellations, hotel.revenue, hotel.amenities.all()
    #         )
    #
    #     def to_dtos_list(self, hotels) -> List[HotelItemDto]:
    #         return [self.to_dto(hotel) for hotel in hotels]
