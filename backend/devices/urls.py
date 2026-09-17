from django.urls import path
from .views import DeviceTelemetryView

urlpatterns = [
    path('sensor-data/', DeviceTelemetryView.as_view(), name='device-sensor-data'),
]
