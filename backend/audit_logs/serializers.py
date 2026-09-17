from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True, default='System')

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'entity',
            'entity_id', 'timestamp', 'metadata'
        ]
