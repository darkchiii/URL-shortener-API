from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from ..models import ShortUrl, Visit
from ..serializers import VisitSerializer


class TestVisitSerializer(TestCase):
    def test_invalid_ip(self):
        short = ShortUrl.objects.create(original_url='...', short_url='abc123')

        data = {
            'pk': short.pk ,
            'ip_address': '999.999.999.999',
            'user_agent': 'TestAgent'
        }

        serializer = VisitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ip_address', serializer.errors)

    def test_missing_user_agent(self):
        short = ShortUrl.objects.create(original_url='https://example.com', short_url='abc123')

        data = {
            'short_url': short.pk,
            'ip_address': '127.0.0.1',
            'user_agent': None
        }

        serializer = VisitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_agent', serializer.errors)

    def test_valid_data(self):
        short = ShortUrl.objects.create(original_url='https://example.com', short_url='abc123')

        data = {
            'short_url': short.pk,
            'ip_address': '127.0.0.1',
            'user_agent': 'TestAgent'
        }

        serializer = VisitSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})
