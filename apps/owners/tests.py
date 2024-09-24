import datetime

from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase

from .models import Owner
from ..destinations.models import Country
from ..users.models import User


class ModelsUnitTest(TestCase):

    def test_create_owner(self):
        user = User.objects.get(pk=2)
        country = Country.objects.get(pk=1)
        owner = Owner.objects.create_owner(
            user=user,
            first_name='Yusuf',
            last_name='Mohammed',
            birthday=datetime.date.today(),
            country_code=country,
            phone='123456789',
            country=country
        )
        self.assertIsInstance(owner, Owner)
        self.assertEqual(owner.first_name, 'Yusuf')


class APIViewsUnitTest(APITestCase):

    def setUp(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='test1234',
            is_active=True
        )
        free_palestine = Country.objects.create(
            name='Palestine',
            country_code=970
        )
        owner = Owner.objects.create_owner(
            user=user,
            first_name='Ali',
            last_name='Ahmed',
            birthday=datetime.date.today(),
            country_code=free_palestine,
            phone=1234567,
            country=free_palestine
        )

    def test_login_owner(self):
        response: WSGIRequest = self.client.post(reverse('login-owner'), {
            'email': 'test@example.com',
            'password': 'test1234'
        })
        self.assertEqual(response.status_code, 200)
