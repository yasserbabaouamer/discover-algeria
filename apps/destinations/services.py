from django.db.models import Count, QuerySet

from apps.destinations.models import City


def get_top_destinations() -> QuerySet:
    cities = City.objects.annotate(
        reservations_count=Count('hotels__room_types__reservations')
    ).order_by('-reservations_count')
    return cities

