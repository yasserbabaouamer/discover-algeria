import typing
from dataclasses import dataclass
from datetime import datetime, date, time
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
class BaseAmenityDTO:
    id: int
    name: str
    icon: str


@dataclass
class BaseAmenityCategory:
    id: int
    name: str
    amenities: List[BaseAmenityDTO]


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
class BaseHotelDTO:
    id: int
    name: str
    stars: int
    address: str
    longitude: float
    latitude: float
    website_url: str
    cover_img: str
    about: str
    business_email: str
    contact_number: str


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
    amenities: typing.List[BaseAmenityDTO]
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
    total: int
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
class AmenityDTO(BaseAmenityDTO):
    checked: bool


@dataclass
class StaffLanguageDTO:
    id: int
    language: str
    checked: bool


@dataclass
class HotelInfoDTO(BaseHotelDTO):
    current_city_id: int
    current_country_code_id: int
    country_codes: List[CountryCodeDTO]
    cities: List[BaseCityDTO]
    facilities: List[AmenityDTO]
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
    parking_available: bool
    reservation_needed: bool
    parking_types: List[ParkingTypeDTO]


@dataclass
class HotelRulesDTO:
    # Define fields for HotelRulesDTO
    cancellation_policies: List[HotelCancellationPolicyDTO]
    prepayment_policies: List[HotelPrepaymentPolicyDTO]


@dataclass
class ImageDTO:
    id: int
    url: str


@dataclass
class HotelEditInfoDTO(BaseHotelDTO):
    current_city_id: int
    current_country_id: int
    current_country_code_id: int
    country_codes: List[CountryCodeDTO]
    cities: List[BaseCityDTO]
    facilities: List[AmenityDTO]
    staff_languages: List[StaffLanguageDTO]
    check_in_from: time
    check_in_until: time
    check_out_from: time
    check_out_until: time
    cancellation_policies: List[HotelCancellationPolicyDTO]
    days_before_cancellation: int
    prepayment_policies: List[HotelPrepaymentPolicyDTO]
    parking_available: bool
    reservation_needed: bool
    parking_types: List[ParkingTypeDTO]
    images: List[ImageDTO]


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
    facilities: List[AmenityDTO]
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


@dataclass
class RoomCancellationPolicyDTO:
    policy: str
    checked: bool


@dataclass
class RoomPrepaymentPolicyDTO:
    policy: str
    checked: bool


@dataclass
class CreateRoomInfoDTO:
    room_types: List[str]
    amenities: List[AmenityDTO]
    cancellation_policies: List[RoomCancellationPolicyDTO]
    prepayment_policies: List[RoomPrepaymentPolicyDTO]


@dataclass
class RoomEditInfoDTO:
    selected_room_type: str
    number_of_rooms: int
    number_of_guests: int
    price_per_night: int
    size: int
    room_types: List[str]
    amenities: List[AmenityDTO]
    cancellation_policies: List[RoomCancellationPolicyDTO]
    days_before_cancellation: int
    prepayment_policies: List[RoomPrepaymentPolicyDTO]
    beds: List[RoomTypeBed]
    cover_img: str
    images: List[ImageDTO]


@dataclass
class EssentialHotelDTO:
    id: int
    name: str
    today_check_ins: int
    reservations_count: int


@dataclass
class ReservationDTO:
    id: int
    username: str
    profile_pic: str
    status: str
    total_price: int


@dataclass
class DailyIncomeDTO:
    date: date
    income: int


@dataclass
class OwnerDashboardDTO:
    hotels: List[EssentialHotelDTO]
    reviews: List[ReviewDTO]
    reservations: List[ReservationDTO]
    daily_incomes: List[DailyIncomeDTO]
