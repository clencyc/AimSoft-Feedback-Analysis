from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    ROLE_NAME_CHOICES = [
        ('sysadmin', 'System Administrator'),
        ('Secondary Stakeholder', 'Support Team'),
    ]
    role_name=models.CharField(max_length=50, choices=ROLE_NAME_CHOICES, default='Secondary Stakeholder')
    name=models.CharField(max_length=255, blank=True, default='')
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role_name = 'sysadmin'
        elif self.is_staff:
            self.role_name = 'Secondary Stakeholder'
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.username} ({self.role_name})"


