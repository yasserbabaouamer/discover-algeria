from dataclasses import dataclass
from typing import List

from apps.destinations.models import CityImage
from apps.hotels.models import HotelImage


@dataclass
class RatingDTO:
    number_of_reviews: int
    avg_rating: int


@dataclass
class HotelDTO:
    id: int
    name: str
    reviews_count: int
    rating_avg: float
    cover_img: str
    images: List[str]
    starts_at: int


@dataclass
class TourDTO:
    id: int
    title: str
    cover_img: str
    rating_avg: float
    reviews_count: int
    starts_at: int


@dataclass
class CityDetailsDTO:
    id: int
    name: str
    description: str
    cover_img: str
    images: List[str]
    hotels: List[HotelDTO]
    tours: List[TourDTO]
