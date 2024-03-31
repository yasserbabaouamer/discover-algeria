import unittest

from .models import *


class HotelsUnitTest(unittest.TestCase):

    def test_get_categories(self):
        r = AmenityCategory.objects.get_categories_by_room_type_id(1)
        for res in r:
            print(res.name)
