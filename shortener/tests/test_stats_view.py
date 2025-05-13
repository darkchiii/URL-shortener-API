
from datetime import timedelta
from django.utils import timezone

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from ..models import ShortUrl, Visit

class StatsViewRetrieveTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.short_url = ShortUrl.objects.create(
            original_url='https://example.com',
            short_url='abc123',
            visits=3,
            expires_at=timezone.now() + timedelta(days=5),
        )
        self.url_retrieve = reverse('stats-detail', args=[self.short_url.pk])

        Visit.objects.create(
            short_url=self.short_url,
            ip_address='127.0.0.1',
            user_agent='TestAgent',
        )
        Visit.objects.create(
            short_url=self.short_url,
            ip_address='192.168.0.1',
            user_agent='TestAgent2',
        )

    def test_visit_stats_response(self):
        response = self.client.get(self.url_retrieve)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Visits", response.json())
        self.assertIn("Last visitor", response.json())