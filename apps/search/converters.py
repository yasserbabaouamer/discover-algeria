from typing import List

from apps.destinations.models import City
from apps.hotels.models import Hotel
from apps.search.dtos import SearchItem
from apps.touristicagencies.models import PeriodicTour, TouristicAgency


class SearchItemConverter:
    # Hotels
    def convert_hotel_to_dto(self, hotel: Hotel) -> SearchItem:
        return SearchItem(
            hotel.id, 'hotel', hotel.cover_img.url, hotel.name,
            f"{hotel.address} , {hotel.city.name} , {hotel.city.country.name}",
            hotel.name_ratio
        )

    def convert_hotels_to_dtos_list(self, hotels) -> List[SearchItem]:
        return [self.convert_hotel_to_dto(hotel) for hotel in hotels]

    # Tours
    def convert_tour_to_dto(self, tour: PeriodicTour) -> SearchItem:
        return SearchItem(
            tour.id, 'tour', tour.cover_img.url, tour.title,
            f"{tour.city.name}, {tour.city.country.name}", tour.title_ratio
        )

    def convert_tours_to_dtos_list(self, tours) -> List[SearchItem]:
        return [self.convert_tour_to_dto(tour) for tour in tours]

    # Tourism Agencies
    def convert_agency_to_dto(self, agency: TouristicAgency) -> SearchItem:
        return SearchItem(
            agency.id, 'agency', agency.cover_img.url, agency.name,
            f"{agency.address}, {agency.city.name}, {agency.city.country.name}",
            agency.name_ratio
        )

    def convert_agencies_to_dtos_list(self, agencies) -> List[SearchItem]:
        return [self.convert_agency_to_dto(agency) for agency in agencies]

    # Cities
    def convert_city_to_dto(self, city: City) -> SearchItem:
        return SearchItem(
            city.id, 'destination', city.cover_img.url, city.name, city.country.name, city.name_ratio
        )

    def convert_cities_to_dtos_list(self, cities):
        return [self.convert_city_to_dto(city) for city in cities]
