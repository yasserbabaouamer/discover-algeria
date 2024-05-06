from apps.destinations.dtos import *
from apps.destinations.models import City
from apps.hotels.models import Hotel
from apps.touristicagencies.models import PeriodicTour


class HotelDtoConverter:
    def convert_hotel_to_dto(self, hotel: Hotel) -> HotelDTO:
        return HotelDTO(
            hotel.id, hotel.name, hotel.reviews_count, hotel.rating_avg, hotel.cover_img.url,
            hotel.images.values_list('img', flat=True), hotel.starts_at
        )

    def convert_hotels_to_dtos_list(self, hotels) -> List[HotelDTO]:
        return [self.convert_hotel_to_dto(hotel) for hotel in hotels]


class TourDtoConverter:
    def convert_tour_to_dto(self, tour: PeriodicTour) -> TourDTO:
        return TourDTO(
            id=tour.id,
            title=tour.title,
            cover_img=tour.cover_img.url,
            rating=RatingDTO(tour.number_of_reviews, tour.avg_rating),
            starts_at=tour.price
        )

    def convert_tours_to_dtos_list(self, tours) -> List[TourDTO]:
        return [self.convert_tour_to_dto(tour) for tour in tours]


class CityDtoConverter:
    def convert_city_to_dto(self, city: City) -> CityDetailsDTO:
        hotel_converter = HotelDtoConverter()
        tour_converter = TourDtoConverter()
        return CityDetailsDTO(
            city.id, city.name, city.description, city.cover_img.url, [image.url for image in city.images.all()],
            hotel_converter.convert_hotels_to_dtos_list(Hotel.objects.find_top_hotels_by_city_id(city.id)),
            tour_converter.convert_tours_to_dtos_list(PeriodicTour.objects.find_top_tours_by_city_id(city.id)),
        )
