from .models import PeriodicTour


def get_top_tours():
    return PeriodicTour.objects.find_top_tours()
