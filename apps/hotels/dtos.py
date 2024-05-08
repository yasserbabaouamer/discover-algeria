import datetime
import typing
from dataclasses import dataclass
from typing import List

from apps.hotels.models import Amenity, BedType, AmenityCategory, GuestReview, RoomTypeBed


@dataclass
class ReviewDTO:
    id: int
    username: str
    profile_pic: str
    title: str
    content: str
    rating: int
    created_at: datetime.datetime


@dataclass
class AmenityDTO:
    id: int
    name: str
    icon: str


@dataclass
class BaseAmenityCategory:
    id: int
    name: str
    amenities: List[AmenityDTO]


@dataclass
class RoomTypeDTO:
    id: int
    name: str
    size: float
    cover_img: str
    beds: List[RoomTypeBed]
    price_per_night: int
    number_of_guests: int
    available_rooms_count: int
    categories: List[BaseAmenityCategory]


@dataclass
class OwnerEssentialInfoDTO:
    first_name: str
    last_name: str
    profile_pic: str


@dataclass
class HotelDetailsDTO:
    id: int
    name: str
    stars: int
    address: str
    starts_at: int
    number_of_reviews: int
    avg_ratings: float
    longitude: float
    latitude: float
    website_url: str
    cover_img: str
    about: str
    business_email: str
    contact_number: str
    owner: OwnerEssentialInfoDTO
    amenities: typing.List[AmenityDTO]
    images: List[str]


@dataclass
class AmenityParamDto:
    name: str
    param: str


@dataclass
class AmenityCategoryDto:
    name: str
    amenities: List[AmenityParamDto]


@dataclass
class HotelDashboardReservationDto:
    completed: int
    cancelled: int
    income: int


@dataclass
class HotelDashboardRoomTypeDto:
    id: int
    rooms_count: int
    occupied_rooms_count: int
    revenue_month: int


@dataclass
class HotelDashboardInfoDto:
    id: int
    name: str
    stars: int
    address: str
    longitude: float
    latitude: float
    rating_avg: float
    reservations: HotelDashboardReservationDto
    room_types: List[HotelDashboardRoomTypeDto]
    reviews: List[GuestReview]


@dataclass
class CountryCodeDTO:
    id: int
    name: str
    country_code: int


@dataclass
class CityDTO:
    id: int
    name: str


@dataclass
class FacilityDTO(AmenityDTO):
    checked: bool


@dataclass
class StaffLanguageDTO:
    id: int
    language: str
    checked: bool


@dataclass
class HotelInfoDTO:
    current_country_code: str
    country_codes: List[CountryCodeDTO]
    cities: List[CityDTO]
    facilities: List[FacilityDTO]
    staff_languages: List[StaffLanguageDTO]


@dataclass
class HotelCancellationPolicyDTO:
    policy: str
    checked: bool


@dataclass
class HotelPrepaymentPolicyDTO:
    policy: str
    checked: bool


@dataclass
class ParkingTypeDTO:
    type: str
    checked: bool


@dataclass
class HotelParkingSituationDTO:
    parking_types: List[ParkingTypeDTO]


@dataclass
class HotelRulesDTO:
    # Define fields for HotelRulesDTO
    cancellation_policies: List[HotelCancellationPolicyDTO]
    prepayment_policies: List[HotelPrepaymentPolicyDTO]


@dataclass
class HotelEditInfoDTO:
    hotel_info: HotelInfoDTO
    hotel_rules: HotelRulesDTO
    parking: HotelParkingSituationDTO
