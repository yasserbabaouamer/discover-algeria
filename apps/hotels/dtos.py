import datetime
import typing
from dataclasses import dataclass
from typing import List

from apps.hotels.models import Amenity, BedType, AmenityCategory


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
