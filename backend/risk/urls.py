from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RiskPredictionViewSet

router = DefaultRouter()
router.register(r'', RiskPredictionViewSet, basename='risk-prediction')

urlpatterns = [
    path('', include(router.urls)),
]
