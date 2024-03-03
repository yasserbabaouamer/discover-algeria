from django.db.models import Count, QuerySet, Avg, Min

from apps.hotels.models import Hotel


def get_most_visited_hotels() -> QuerySet:
    return Hotel.objects.annotate(
        reservations_count=Count('room_types__reservations'),
        rating=Avg('room_types__reservations__review__rating'),
        starts_at=Min('room_types__price_per_night')
    ).order_by('-reservations_count')
