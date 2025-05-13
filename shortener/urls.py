from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShortUrlViewSet,VisitViewSet

router = DefaultRouter()
router.register(r'shortener', ShortUrlViewSet, basename='shortener')
router.register(r'stats', VisitViewSet, basename='stats')

urlpatterns = [
    path('api/', include(router.urls)),
]