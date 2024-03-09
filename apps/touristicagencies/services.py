from .models import Tour


def get_top_tours():
    return Tour.objects.get_top_tours()
