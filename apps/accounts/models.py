from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from core.models import BaseModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModel):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('broker', 'Broker'),
        ('admin', 'Admin'),
    )

    # Remove the default username field entirely — we use email-only auth
    username = None

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    full_name = models.CharField(max_length=120)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    fcm_token = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

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
