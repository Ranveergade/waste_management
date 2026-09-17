from rest_framework import serializers
from .models import VisionEvent

class VisionEventSerializer(serializers.ModelSerializer):
    container_id = serializers.CharField(source='container.container_id', read_only=True)

    class Meta:
        model = VisionEvent
        fields = [
            'id', 'container', 'container_id', 'timestamp',
            'predicted_class', 'confidence', 'contamination_score',
            'unknown_probability', 'exception_reason'
        ]
