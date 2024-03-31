from concurrent.futures import ProcessPoolExecutor
from functools import partial
from multiprocessing.pool import Pool
from typing import List

from apps.hotels.models import Hotel
from apps.search.dtos import SearchItem

from .converters import SearchItemConverter
from ..destinations.models import City
from ..touristicagencies.models import Tour, TouristicAgency

converter = SearchItemConverter()


def search_hotels(keyword) -> List[SearchItem]:
    hotels = Hotel.objects.find_by_keyword(keyword)
    print(f"Hotels having keyword {keyword} are : {hotels}")
    return converter.convert_hotels_to_dtos_list(hotels)


def search_agencies(keyword) -> List[SearchItem]:
    agencies = TouristicAgency.objects.find_by_keyword(keyword)
    return converter.convert_agencies_to_dtos_list(agencies)


def search_tours(keyword) -> List[SearchItem]:
    print("Going to fetch tours")
    tours = Tour.objects.find_by_keyword(keyword)
    print(tours)
    return converter.convert_tours_to_dtos_list(tours)


def search_cities(keyword) -> List[SearchItem]:
    cities = City.objects.find_by_keyword(keyword)
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
        futures = [executor.submit(f, keyword) for f in [search_hotels, search_tours, search_agencies, search_cities]]
        for future in futures:
            results.extend(future.result())
    return quicksort(results)
