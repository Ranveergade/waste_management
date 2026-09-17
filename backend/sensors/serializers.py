from rest_framework import serializers
from .models import SensorReading

class SensorReadingSerializer(serializers.ModelSerializer):
    container_id = serializers.CharField(source='container.container_id', read_only=True)

    class Meta:
        model = SensorReading
        fields = [
            'id', 'container', 'container_id', 'timestamp', 'weight',
            'fill_level', 'temperature', 'humidity', 'gas_indicator',
            'moisture', 'device_status'
        ]
