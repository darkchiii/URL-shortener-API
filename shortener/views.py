from django.shortcuts import redirect, render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ShortUrlSerializer, VisitSerializer
from .models import ShortUrl, Visit
from django.utils import timezone
from time import time
import ipaddress
import hashlib

def generate_short_code(original_url, length):
    hash_object = hashlib.sha256(original_url.encode())
    short_hash = hash_object.hexdigest()[:length]
    return short_hash

class ShortUrlViewSet(viewsets.ViewSet):
    def create(self, request):
        original_url = request.data.get('original_url')
        try:
            existing_url = ShortUrl.objects.get(original_url=original_url)
            return Response({"short_url": existing_url.short_url,
                                 "status": "URL already exists"},
                                status=status.HTTP_200_OK)
        except ShortUrl.DoesNotExist:
            serializer = ShortUrlSerializer(data=request.data)
            if serializer.is_valid():
                    short_code = generate_short_code(original_url, 8)

                    while True:
                        try:
                            ShortUrl.objects.get(short_url=short_code)
                            short_code = generate_short_code(original_url + str(time.time()))
                        except ShortUrl.DoesNotExist:
                            break

                    short_url = ShortUrl.objects.create(original_url=original_url, short_url=short_code)
                    return Response({"short_url": short_code,
                                    "status": "short URL created"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            url_obj = ShortUrl.objects.get(short_url = pk)
            url_obj.visits += 1
            url_obj.save()

            ip_address = request.META.get('REMOTE_ADDR', 'unknown')
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')

            try:
                ip_address_obj = ipaddress.ip_address(ip_address)
            except ValueError:
                ip_address = 'invalid'

            data={
                'short_url': url_obj.pk,
                'ip_address': ip_address,
                'user_agent': user_agent
            }

            # print("visit serializer data", data)
            # print("request.meta: ", request.META)

            serializer = VisitSerializer(data=data)
            if serializer.is_valid():

                serializer.save()
                return redirect(url_obj.original_url)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # return redirect(url_obj.original_url)
        except ShortUrl.DoesNotExist:
            return Response({"error": "Short URL not found"},
                            status=status.HTTP_404_NOT_FOUND)


class VisitViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        try:
            short_obj = ShortUrl.objects.get(pk=pk)
            visits_counter = short_obj.visits
            last_visitor = Visit.objects.filter(short_url=short_obj).order_by('-visited_at').first()

            if last_visitor is not None:
                pass
            else:
                last_visitor = 'No data yet!'

            if short_obj.is_active:
                delta = short_obj.expires_at - timezone.now()
                days_left = delta.days
            else:
                days_left = 0
            active = short_obj.is_active

            return Response({"Short url": short_obj.short_url,
                             "Visits": visits_counter,
                             "Active":  active,
                             "Days left": days_left,
                             "Last visitor": last_visitor.visited_at,
            })

        except ShortUrl.DoesNotExist:
            return Response({"error": "Short URL not found"},
                            status=status.HTTP_404_NOT_FOUND)



