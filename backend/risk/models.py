from django.db import models
from containers.models import Container

class RiskLevel(models.TextChoices):
    LOW = 'LOW', 'Low Risk'
    MEDIUM = 'MEDIUM', 'Medium Risk'
    HIGH = 'HIGH', 'High Risk'
    CRITICAL = 'CRITICAL', 'Critical Risk'

class RiskPrediction(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE, related_name='risk_predictions')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    risk_score = models.IntegerField(help_text='Calculated risk score 0 to 100')
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW)
    recommended_action = models.CharField(max_length=50, help_text='Operational action recommendation')
    reason = models.TextField(help_text='Detailed clinical and sensor rationale for recommendation')
    model_version = models.CharField(max_length=30, default='RiskEngine-v1.2-RuleSystem')

    class Meta:
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'

    def __str__(self):
        return f"{self.container.container_id} Risk: {self.risk_level} ({self.risk_score}/100) -> {self.recommended_action}"
