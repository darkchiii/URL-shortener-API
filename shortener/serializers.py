from rest_framework import serializers
from .models import ShortUrl, Visit
from django.core.validators import RegexValidator
# import re


class ShortUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortUrl
        fields = ['original_url', 'short_url']
        extra_kwargs = {
            'original_url': {'required': True, 'max_length': 2000 },
            'short_url': {'required': False, 'validators': [
                RegexValidator(regex=r'^[a-zA-Z0-9]+$', message='Short URL może zawierać tylko litery i cyfry.')
            ]}

        }
    # def validate_short_url(self, value):
    #     if not re.match(r'^[A-Za-z0-9_-]+$', value):
    #         raise serializers.ValidationError('Short URL może zawierać tylko litery i cyfry.')
    #     return value

class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = ['short_url', 'ip_address', 'user_agent']