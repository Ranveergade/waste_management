from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=100, db_index=True, help_text='Event action name e.g. RISK_LEVEL_CHANGED, ISOLATION_CONFIRMED')
    entity = models.CharField(max_length=50, help_text='Target entity e.g. Container, Action, Alert')
    entity_id = models.CharField(max_length=100, help_text='Target entity ID or container_id')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True, help_text='Extra event context payload')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.action} on {self.entity} #{self.entity_id} by {self.user.username if self.user else 'System'}"
