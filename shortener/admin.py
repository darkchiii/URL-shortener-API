from django.contrib import admin

# Register your models here.
from .models import ShortUrl, Visit

admin.site.register(ShortUrl)
admin.site.register(Visit)