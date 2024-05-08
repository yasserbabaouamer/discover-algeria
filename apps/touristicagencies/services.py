from datetime import date

from .models import PeriodicTour


def get_top_tours():
    return PeriodicTour.objects.find_top_tours()


def find_available_tours(city_id: int, filter_request: dict):
    current_day: date = filter_request['check_in']
    days = {}
    while current_day <= filter_request['check_out']:
        weekday = current_day.today().strftime('%A')
        if weekday not in days:
            days[weekday] = [current_day]
        days[weekday].append(current_day)
    print('Requested Days :', days)
    return PeriodicTour.objects.find_available_tours_by_city_id(city_id, days)
