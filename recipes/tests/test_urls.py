from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class StaticURLTests(TestCase):
    NAME = 'AuthTestUser'

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_user = User.objects.create_user(
            username=self.NAME
        )
        self.auth_client.force_login(self.auth_user)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_personal_page(self):
        response = self.auth_client.get(
            reverse('profile', kwargs={'user_id': 1})
        )
        self.assertEqual(response.status_code, 200)
