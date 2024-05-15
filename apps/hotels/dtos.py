import typing
from dataclasses import dataclass
from datetime import datetime
from typing import List

from apps.hotels.models import GuestReview, RoomTypeBed, RoomTypePolicies, HotelRules


@dataclass
class ReviewDTO:
    id: int
    username: str
    profile_pic: str
    title: str
    content: str
    rating: int
    created_at: datetime


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
    policies: RoomTypePolicies


@dataclass
class OwnerEssentialInfoDTO:
    id: int
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
    reviews_count: int
    rating_avg: float
    longitude: float
    latitude: float
    website_url: str
    cover_img: str
    about: str
    business_email: str
    contact_number: str
    owner: OwnerEssentialInfoDTO
    amenities: typing.List[AmenityDTO]
    rules: HotelRules
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
    name: str
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
class BaseCityDTO:
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
    cities: List[BaseCityDTO]
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


@dataclass
class CityDTO(BaseCityDTO):
    checked: bool
    country_id: int


@dataclass
class CountryDTO:
    id: int
    name: str
    checked: bool


@dataclass
class HotelCreateInfoDTO:
    countries: List[CountryDTO]
    cities: List[CityDTO]
    languages: List[StaffLanguageDTO]
    facilities: List[FacilityDTO]
    cancellation_policies: List[HotelCancellationPolicyDTO]
    prepayment_policies: List[HotelPrepaymentPolicyDTO]
    parking_types: List[ParkingTypeDTO]


@dataclass
class ReservedRoomTypeDTO:
    name: str
    quantity: int


@dataclass
class HotelEssentialDTO:
    id: int
    name: str


@dataclass
class GuestReservationDTO:
    id: int
    total_price: int
    check_in: datetime
    check_out: datetime
    created_at: datetime
    hotel: HotelEssentialDTO
    reserved_room_types: List[ReservedRoomTypeDTO]

