
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from ..models import ShortUrl

class ShortUrlModelTests(TestCase):
    def create_shorturl_model(self, original_url='https://docs.djangoproject.com/en/5.2/topics/testing/overview/'):
        return ShortUrl.objects.create(original_url=original_url)

    def test_shorturl_creation(self):
        short_url = self.create_shorturl_model()
        self.assertTrue(isinstance(short_url, ShortUrl))

