from django.db import models
from django.contrib.auth.models import User

class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    SUPERVISOR = 'SUPERVISOR', 'Supervisor'
    OPERATOR = 'OPERATOR', 'Operator'
    SAFETY_OFFICER = 'SAFETY_OFFICER', 'Safety Officer'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OPERATOR)
    employee_id = models.CharField(max_length=50, unique=True)
    ward_assigned = models.CharField(max_length=100, blank=True, null=True, help_text="Primary assigned hospital ward")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role}) - ID: {self.employee_id}"
