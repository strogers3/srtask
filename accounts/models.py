from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with timezone and preferences."""
    email = models.EmailField(unique=True)
    timezone = models.CharField(max_length=50, default='America/Jamaica')
    preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.email
