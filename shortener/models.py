from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone

def get_expiration_date():
    return timezone.now() + timedelta(days=7)

class ShortUrl(models.Model):
    original_url = models.URLField(unique=True, max_length=2000)
    short_url = models.CharField(max_length=8, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    visits = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(default=get_expiration_date, db_index=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.short_url} -> {self.original_url}"

    class Meta:
        ordering = ['-created_at']

class Visit(models.Model):
    short_url = models.ForeignKey(ShortUrl, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    visited_at = models.DateTimeField(auto_now_add=True)