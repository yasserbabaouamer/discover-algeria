from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, time
from typing import List

from apps.hotels.models import Hotel
from apps.search.dtos import SearchItem
from .converters import SearchItemConverter
from ..destinations.models import City
from ..touristicagencies.models import PeriodicTour, TouristicAgency

# Quick Search Part

converter = SearchItemConverter()


def do_quick_search_hotels(keyword) -> List[SearchItem]:
    hotels = Hotel.objects.find_by_keyword(keyword)
    return converter.convert_hotels_to_dtos_list(hotels)


def do_quick_search_agencies(keyword) -> List[SearchItem]:
    agencies = TouristicAgency.objects.find_by_keyword(keyword)
    return converter.convert_agencies_to_dtos_list(agencies)


def do_quick_search_tours(keyword) -> List[SearchItem]:
    tours = PeriodicTour.objects.find_by_keyword(keyword)
    print(tours)
    return converter.convert_tours_to_dtos_list(tours)


def do_quick_search_cities(keyword) -> List[SearchItem]:
    cities = City.objects.find_by_keyword(keyword)
    for city in cities:
        print(f"{city.name} : {city.name_ratio}")
    return converter.convert_cities_to_dtos_list(cities)


def quicksort(arr: List[SearchItem]) -> List[SearchItem]:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2].relevance
    left = [item for item in arr if item.relevance < pivot]
    middle = [item for item in arr if item.relevance == pivot]
    right = [item for item in arr if item.relevance > pivot]
    return quicksort(right) + middle + quicksort(left)


def do_quick_search(keyword: str) -> List[SearchItem]:
    results = []
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(f, keyword) for f in
                   [do_quick_search_hotels, do_quick_search_tours, do_quick_search_agencies, do_quick_search_cities]]
        for future in futures:
            results.extend(future.result())
    return quicksort(results)


# Detailed Search By City Part

def get_available_hotels_by_city(search_request: dict):
    check_in = datetime.combine(search_request['check_in'], time(13, 0))
    check_out = datetime.combine(search_request['check_out'], time(12, 0))
    hotels = Hotel.objects.find_available_hotels_by_city_id(search_request['city_id'])
    pass


