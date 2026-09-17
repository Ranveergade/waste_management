from rest_framework import serializers
from .models import Alert

class AlertSerializer(serializers.ModelSerializer):
    container_id = serializers.CharField(source='container.container_id', read_only=True)
    location = serializers.CharField(source='container.location', read_only=True)
    ward = serializers.CharField(source='container.ward', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'container', 'container_id', 'location', 'ward',
            'severity', 'alert_type', 'message', 'recommended_action',
            'status', 'created_at', 'resolved_at'
        ]
