from dataclasses import dataclass
from datetime import date, time


@dataclass
class TourDetailsDTO:
    id: int
    title: str
    description: str
    number_of_reviews: int
    avg_ratings: float
    touristic_agency: str
    cover_img: str
    start_day: str
    start_time: time
    end_day: str
    end_time: time
    city: str
    price: int
