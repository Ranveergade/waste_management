from django.db import models
from django.contrib.auth.models import User
from containers.models import Container

class CollectionStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class CollectionRecord(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE, related_name='collection_records')
    worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collections_handled')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    weight_collected = models.FloatField(default=0.0, help_text='Actual weight collected in kg')
    fill_at_collection = models.FloatField(default=0.0, help_text='Fill percentage at collection time')
    status = models.CharField(max_length=20, choices=CollectionStatus.choices, default=CollectionStatus.SCHEDULED)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Collection for {self.container.container_id} by {self.worker.username if self.worker else 'Unassigned'} ({self.status})"
