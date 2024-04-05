from dataclasses import dataclass

from typing import List

from apps.hotels.models import Amenity


@dataclass
class SearchItem:
    id: int
    type: str
    image: str
    name: str
    address: str
    relevance: float


@dataclass
class HotelItem:
    id: int
    name: str
    rating: float
    starts_from: int
    hotel_amenities: List[Amenity]
    is_liked: bool
