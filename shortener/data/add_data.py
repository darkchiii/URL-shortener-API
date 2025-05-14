import csv
import os
from django.conf import settings
from ..models import ShortUrl

def import_urls_from_csv():
    file_path = os.path.join(settings.BASE_DIR, 'shortener', 'data', 'urls_data.csv')

    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            original_url = row['original_url']
            ShortUrl.objects.create(original_url = original_url)

