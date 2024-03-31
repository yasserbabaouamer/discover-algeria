import unittest

from django.test import TestCase

from apps.destinations import services


# Create your tests here.

class UserTests(TestCase):
    def get_top_destinations(self):
        destinations = services.get_top_destinations()
        print(destinations)



if __name__ == '__main__':
    unittest.main()
