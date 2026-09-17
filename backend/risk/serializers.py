from rest_framework import serializers
from .models import RiskPrediction

class RiskPredictionSerializer(serializers.ModelSerializer):
    container_id = serializers.CharField(source='container.container_id', read_only=True)

    class Meta:
        model = RiskPrediction
        fields = [
            'id', 'container', 'container_id', 'timestamp',
            'risk_score', 'risk_level', 'recommended_action',
            'reason', 'model_version'
        ]
