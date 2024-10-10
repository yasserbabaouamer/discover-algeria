from datetime import date, timedelta

from django.shortcuts import get_object_or_404

from .models import PeriodicTour


def get_top_tours():
    return PeriodicTour.objects.find_top_tours()


def find_available_tours(city_id: int, filter_request: dict):
    current_date: date = filter_request['check_in']
    days = {}
    while current_date <= filter_request['check_out']:
        # The user passes the starting and ending dates
        # I get the day names of this period
        # Find the available tours which happen on those days
        weekday = current_date.today().strftime('%A')
        if weekday not in days:
            days[weekday] = [current_date]
        else:
            days[weekday].append(current_date)
        current_date += timedelta(days=1)
    print('Requested Days :', days)
    return PeriodicTour.objects.find_available_tours_by_city_id(city_id, days)


def find_tour_by_id(tour_id):
    return PeriodicTour.objects.find_by_id(tour_id)
