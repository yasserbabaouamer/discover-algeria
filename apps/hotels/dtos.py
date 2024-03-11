import datetime
import typing
from dataclasses import dataclass

from apps.hotels.models import Amenity


@dataclass
class ReviewDTO:
    id: int
    title: str
    content: str
    created_at: datetime.datetime


@dataclass
class AmenityDTO:
    id: int
    name: str
    icon: str


@dataclass
class HotelDetailsDTO:
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
    amenities: typing.List[AmenityDTO]