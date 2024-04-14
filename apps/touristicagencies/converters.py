from .models import PeriodicTour
from .dtos import *

# class TourDetailsDtoConverter:
#     def to_dto(self,tour:PeriodicTour) -> TourDetailsDTO:
#         return TourDetailsDTO(
#             tour.id, tour.title, tour.description, tour.number_of_reviews, tour.avg_ratings, tour.touristic_agency.name,
#             tour.cover_img.url, tour.start_day,
#         )

