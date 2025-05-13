
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from ..models import ShortUrl, Visit

class ShortUrlCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url_create = reverse('shortener-list')

    def test_create_short_url_for_valid_input(self):
        data = {
            'original_url': 'https://example.com?param=value'
        }
        response = self.client.post(self.url_create, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('short_url', response.data)
        self.assertTrue(ShortUrl.objects.filter(original_url=data['original_url'],
                                                short_url=response.data['short_url']).exists())
        self.assertEqual(len(response.data['short_url']), 8)

    def test_create_short_url_for_invalid_url(self):
        invalid_urls = [
            '',
            'example.com',
            'http://',
            'https://exa mple.com',
            ' ',
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                response = self.client.post(self.url_create, {'original_url': url}, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertFalse(ShortUrl.objects.filter(original_url=url).exists())
                self.assertIn('original_url', response.data)

    def test_long_url(self):
        base_url = 'https://example.com'
        long_url = base_url + 'a' * (2000 - len(base_url))
        response=self.client.post(self.url_create, {'original_url': long_url}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('original_url', response.data)

    def test_different_http_schemes(self):
        for scheme in ['http://', 'https://']:
            with self.subTest(scheme=scheme):
                url = f"{scheme}example.com"
                response = self.client.post(self.url_create, {'original_url': url}, format='json')
                self.assertEqual(response.status_code, 201)

    def test_existing_url(self):
        existing_url = ShortUrl.objects.create(
            original_url='https://example.com',
            short_url='abc123ab'
        )
        response = self.client.post(self.url_create, {'original_url': 'https://example.com'}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_same_url_returns_same_short_url(self):
        original_url = 'https://example.com/page'

        response1 = self.client.post(self.url_create, {'original_url':original_url}, format='json')
        short_url1 = response1.data['short_url']
        self.assertEqual(response1.status_code, 201)

        response2 = self.client.post(self.url_create, {'original_url': original_url}, format='json')
        short_url2 = response2.data['short_url']
        self.assertEqual(short_url1, short_url2)

        self.assertEqual(ShortUrl.objects.filter(original_url=original_url, short_url=short_url1).count(), 1)

    def test_unique_short_urls_for_different_originals(self):
        original_url1= 'https://example.com/page1'
        response1 = self.client.post(self.url_create, {'original_url':original_url1}, format='json')
        original_url2= 'https://example.com/page2'
        response2 =self.client.post(self.url_create, {'original_url': original_url2}, format='json')

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)

        self.assertNotEqual(response1.data['short_url'], response2.data['short_url'])

    def test_special_chars_in_shorts(self):
        invalid_chars = ['?', '/', '#', ' ', '%', '=']
        for char in invalid_chars:
            short = f'abc{char}123'
            data = {
                'original_url': 'https://example.com/page',
                'short_url': short
            }
            response = self.client.post(self.url_create, data, format='json')
            self.assertEqual(response.status_code,400)
            self.assertFalse(ShortUrl.objects.filter(short_url=data['short_url']).exists())

class ShortUrlRetrieveTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_url = ShortUrl.objects.create(
            original_url='https://example.com',
            short_url='abc123',
            visits=0,
        )
        self.url_retrieve = reverse('shortener-detail', args=[self.test_url.short_url])

    def test_existing_url(self):
        response = self.client.get(self.url_retrieve)
        self.assertEqual(response.status_code, 302)

    def test_multiple_requests(self):

        for _ in range(5):
            response = self.client.get(self.url_retrieve)
            self.assertEqual(response.status_code, 302)

    def test_retrieve_nonexistent_url(self):
        data = {
            "original_url": 'https://example.com123',
            "short_url": 'abc1234',
        }
        response = self.client.get(reverse('shortener-detail', args=[data['short_url']]))
        self.assertEqual(response.status_code, 404)

    def test_redirects_to_original_url(self):
        response = self.client.get(self.url_retrieve, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], self.test_url.original_url)

    def test_visit_counter(self):
        response = self.client.get(self.url_retrieve)
        short_obj = ShortUrl.objects.get(short_url=self.test_url.short_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(short_obj.visits, 1)

    def test_2_visit_counter(self):
        response1 = self.client.get(self.url_retrieve)
        response2 = self.client.get(self.url_retrieve)

        short_obj = ShortUrl.objects.get(short_url=self.test_url.short_url)
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 302)

        self.assertEqual(short_obj.visits, 2)

    def test_visit_instance_created(self):
        response = self.client.get(self.url_retrieve)
        self.assertTrue(Visit.objects.filter(short_url=self.test_url).exists())

    def test_visit_instance_links_to_accurate_short(self):
        response = self.client.get(self.url_retrieve)
        visit = Visit.objects.get(short_url=self.test_url)
        self.assertEqual(visit.short_url, self.test_url)
        self.assertEqual(Visit.objects.count(), 1)

    def test_ip_address_saved(self):
        response = self.client.get(self.url_retrieve)
        visit_obj = Visit.objects.get(short_url=self.test_url)
        self.assertEqual(visit_obj.ip_address, '127.0.0.1')

    def test_invalid_ip_addres(self):
        data = {
            'short_url': self.test_url.short_url,
            'ip_address': 'invalid_ip',
            'user_agent': 'TestAgent'
        }
        response = self.client.get(self.url_retrieve, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Visit.objects.count(), 1)

    def test_missing_user_agent(self):
        data = {
            'short_url': self.test_url.short_url,
            'ip_address': '127.0.0.1',
            'user_agent': ''
        }
        response = self.client.get(self.url_retrieve, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Visit.objects.count(), 1)