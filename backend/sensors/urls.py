from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SensorReadingViewSet

router = DefaultRouter()
router.register(r'', SensorReadingViewSet, basename='sensor-reading')

urlpatterns = [
    path('', include(router.urls)),
]
