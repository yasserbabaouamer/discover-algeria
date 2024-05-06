import datetime
import typing
from dataclasses import dataclass
from typing import List

from apps.hotels.models import Amenity, BedType, AmenityCategory, GuestReview


@dataclass
class ReviewDTO:
    id: int
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
class RoomTypeDTO:
    id: int
    name: str
    size: float
    nb_beds: int
    main_bed_type: BedType
    price_per_night: int
    cover_img: str
    nb_available_rooms: int
    categories: dict


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
    amenities: typing.List[AmenityDTO]


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
