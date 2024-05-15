from .dtos import *
from .enums import HotelCancellationPolicy, HotelPrepaymentPolicy, ParkingType
from .models import Hotel, GuestReview, RoomType, Room, Language, Amenity, AmenityCategory
from ..destinations.models import Country, City


class ReviewDtoConverter:

    def to_dto(self, review: GuestReview) -> ReviewDTO:
        return ReviewDTO(
            review.id, f"{review.reservation.guest.first_name} "
                       f"{review.reservation.guest.last_name}",
            review.reservation.guest.profile_pic.url,
            review.title, review.content, review.rating,
            review.created_at
        )

    def to_dtos_list(self, reviews) -> List[ReviewDTO]:
        return [self.to_dto(review) for review in reviews]


class HotelDetailsDtoConverter:

    def to_dto(self, hotel: Hotel) -> HotelDetailsDTO:
        return HotelDetailsDTO(
            hotel.id, hotel.name, hotel.stars, f"{hotel.address}, {hotel.city.name}, {hotel.city.country.name}",
            hotel.starts_at, hotel.reviews_count, hotel.rating_avg, hotel.longitude, hotel.latitude,
            hotel.website_url, hotel.cover_img.url, hotel.about, hotel.business_email,
            hotel.contact_number, OwnerEssentialInfoDTO(
                hotel.owner.id,
                hotel.owner.first_name,
                hotel.owner.last_name,
                hotel.owner.profile_pic.url
            ), hotel.amenities.all(), hotel.rules, [image.img.url for image in hotel.images.all()]
        )

    def to_dtos_list(self, hotels) -> List[HotelDetailsDTO]:
        return [self.to_dto(hotel) for hotel in hotels]


class BaseAmenityCategoryConverter:
    def to_dto(self, category, amenities) -> BaseAmenityCategory:
        return BaseAmenityCategory(
            category.id, category.name,
            [AmenityDTO(amenity.id, amenity.name, amenity.icon.url) for amenity in amenities]
        )


class RoomTypeConverter:
    amenity_category_converter = BaseAmenityCategoryConverter()

    def to_dto(self, room_type: RoomType) -> RoomTypeDTO:
        categories_dict = RoomType.objects.get_categories_and_amenities(room_type.id)
        return RoomTypeDTO(
            room_type.id, room_type.name, room_type.size, room_type.cover_img.url,
            room_type.beds.all(), room_type.price_per_night,
            room_type.number_of_guests,
            room_type.available_rooms_count,
            [self.amenity_category_converter.to_dto(category, amenities) for category, amenities in
             categories_dict.items()],
            room_type.policies
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
            room_type.id, room_type.name, room_type.rooms_count,
            room_type.occupied_rooms_count, room_type.monthly_revenue
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
            [r.review for r in hotel.reservations.all() if hasattr(r, 'review')]
        )


def get_cancellation_policy_dto(policy: str,
                                selected_policy: str) -> HotelCancellationPolicyDTO:
    return HotelCancellationPolicyDTO(
        policy=policy,
        checked=(policy == selected_policy)
    )


class HotelEditInfoDtoConverter:
    def to_dto(self, hotel: Hotel) -> HotelEditInfoDTO:
        pass
