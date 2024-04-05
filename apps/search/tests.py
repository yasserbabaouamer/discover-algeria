from django.test import TestCase

from apps.search import services


# Create your tests here.

class LTestCase(TestCase):
    def test_search_tours(self):
        result = services.quick_search_tours('Hide')
        print(result)
