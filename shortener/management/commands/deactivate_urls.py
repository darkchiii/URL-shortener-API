from shortener.models import ShortUrl
from django.utils.timezone import now
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Dezaktywuje wygasłe linki"

    def handle(self, *args, **kwargs):
        expired_urls = ShortUrl.objects.filter(expires_at__lt=now(), is_active=True)
        count = expired_urls.update(is_active=False)
        self.stdout.write(self.style.SUCCESS(f"Dezaktywowano {count} linków"))