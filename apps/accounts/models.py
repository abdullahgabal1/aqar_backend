from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel

class User(AbstractUser, BaseModel):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('broker', 'Broker'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    full_name = models.CharField(max_length=120)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    fcm_token = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    def __str__(self):
        return self.email


class UserPreferences(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    min_price = models.BigIntegerField(null=True, blank=True)
    max_price = models.BigIntegerField(null=True, blank=True)
    min_area = models.IntegerField(null=True, blank=True)
    max_area = models.IntegerField(null=True, blank=True)
    bedrooms = models.JSONField(null=True, blank=True)
    property_types = models.JSONField(null=True, blank=True)
    areas = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"
