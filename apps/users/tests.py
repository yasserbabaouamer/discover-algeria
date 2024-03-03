import unittest

from django.conf import settings

from core import settings
from . import services


class UserTests(unittest.TestCase):
    settings.include()
    def login_user(self):
        user = services.authenticate_guest({
            'email': 'yacerbaba10@gmail.com',
            'password': 'yacerbabag'
        })
        print(user)
        assert user is not None
