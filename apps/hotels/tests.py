from django.test import TestCase

from .models import Amenity, Hotel
from ..owners.models import Owner


class ModelsUnitTest(TestCase):

    def test_get_room_amenities(self):
        amenities = Amenity.objects.find_all_rooms_amenities()
        facilities = amenities.filter(category__name='Facilities')
        self.assertEqual(facilities.count(), 0, msg="Boom")

    def test_create_hotel(self):
        owner = Owner.objects.get(pk=1)
        hotel_info = {
            "name": "Testing hotel",
            "address": "Best plans",
            "city_id": "3",
            "stars": 4,
            "about": "This is a desc",
            "country_code_id": 1,
            "contact_number": 674947412,
            "latitude": 38.001,
            "longitude": 38.001
        }
        hotel = Hotel.objects.create(
            owner=owner,
            **hotel_info,
            cover_img=None,
            parking_available=False
        )
        self.assertIsInstance(hotel, Hotel)
