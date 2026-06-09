from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel

User = get_user_model()

class Property(BaseModel):
    PROPERTY_TYPES = (
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('duplex', 'Duplex'),
        ('studio', 'Studio'),
        ('penthouse', 'Penthouse'),
        ('townhouse', 'Townhouse'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('draft', 'Draft'),
    )
    FINISHING_CHOICES = (
        ('super_lux', 'Super Lux'),
        ('lux', 'Lux'),
        ('semi_lux', 'Semi Lux'),
        ('standard', 'Standard'),
        ('core_shell', 'Core & Shell'),
    )

    broker = models.ForeignKey('brokers.BrokerProfile', on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    
    price = models.BigIntegerField()
    area = models.IntegerField()
    bedrooms = models.PositiveSmallIntegerField()
    bathrooms = models.PositiveSmallIntegerField()
    floor = models.IntegerField(null=True, blank=True)
    finishing = models.CharField(max_length=15, choices=FINISHING_CHOICES)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.CharField(max_length=50)
    area_name = models.CharField(max_length=100)
    address = models.TextField(null=True, blank=True)
    
    amenities = models.JSONField(null=True, blank=True)
    payment_plan = models.JSONField(null=True, blank=True)
    
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.price} EGP"


class PropertyImage(BaseModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.property.title}"


class Favorite(BaseModel):
    SOURCE_CHOICES = (
        ('manual', 'Manual'),
        ('ai_suggestion', 'AI Suggestion'),
        ('ai_recommendation', 'AI Recommendation'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    ai_suggestion = models.ForeignKey('ai.AIPropertySuggestion', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.email} saved {self.property.title}"


class VisitRequest(BaseModel):
    VISIT_TYPES = (
        ('in_person', 'In Person'),
        ('virtual', 'Virtual'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visit_requests')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='visit_requests')
    visit_date = models.DateField()
    visit_time = models.TimeField()
    visit_type = models.CharField(max_length=10, choices=VISIT_TYPES)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Visit to {self.property.title} by {self.user.email}"
