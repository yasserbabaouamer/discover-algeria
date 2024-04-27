from django.db.models import Count, QuerySet

from .dtos import *
from .models import City, Country
from .converters import *

city_dto_converter = CityDtoConverter()


def get_top_destinations() -> QuerySet:
    return City.objects.find_top_cities()


def get_city_details_by_id(city_id: int) -> CityDetailsDTO:
    city = City.objects.find_by_id(city_id)
    return city_dto_converter.convert_city_to_dto(city)


def find_all_countries_codes():
    return Country.objects.all()
