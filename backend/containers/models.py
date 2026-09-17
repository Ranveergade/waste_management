from django.db import models

class ContainerStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'

class DeviceStatus(models.TextChoices):
    ONLINE = 'ONLINE', 'Online'
    OFFLINE = 'OFFLINE', 'Offline'

class WasteCategory(models.TextChoices):
    GENERAL = 'GENERAL', 'General Non-Hazardous'
    INFECTIOUS = 'INFECTIOUS', 'Infectious Biomedical'
    SHARPS = 'SHARPS', 'Sharps Waste'
    HAZARDOUS = 'HAZARDOUS', 'Chemical / Hazardous'
    CYTOTOXIC = 'CYTOTOXIC', 'Cytotoxic Waste'
    ANATOMICAL = 'ANATOMICAL', 'Anatomical Waste'

class Container(models.Model):
    container_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    hospital = models.CharField(max_length=150, default='City Central Hospital')
    location = models.CharField(max_length=150, help_text='Specific location room or corridor')
    ward = models.CharField(max_length=100, db_index=True, help_text='Ward / Department (e.g. ICU, Emergency Ward, Surgery)')
    status = models.CharField(max_length=20, choices=ContainerStatus.choices, default=ContainerStatus.ACTIVE)
    capacity_liters = models.FloatField(default=60.0)
    device_status = models.CharField(max_length=20, choices=DeviceStatus.choices, default=DeviceStatus.ONLINE)
    waste_category = models.CharField(max_length=30, choices=WasteCategory.choices, default=WasteCategory.INFECTIOUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['container_id']

    def __str__(self):
        return f"Container {self.container_id} ({self.ward})"
