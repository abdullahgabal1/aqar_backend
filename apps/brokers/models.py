from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel

User = get_user_model()

class BrokerProfile(BaseModel):
    SUBSCRIPTION_PLANS = (
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('elite', 'Elite'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='broker_profile')
    company_name = models.CharField(max_length=200, null=True, blank=True)
    license_number = models.CharField(max_length=50, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_leads = models.IntegerField(default=0)
    subscription_plan = models.CharField(max_length=10, choices=SUBSCRIPTION_PLANS, default='free')
    subscription_expires = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.company_name or self.user.email


class LeadPurchase(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    broker = models.ForeignKey(BrokerProfile, on_delete=models.CASCADE, related_name='lead_purchases')
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='lead_purchases')
    quantity = models.IntegerField()
    price_per_lead = models.IntegerField()
    total_amount = models.IntegerField()
    payment_ref = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    leads_delivered = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.quantity} leads for {self.property.title} by {self.broker.company_name}"


class ListingPromotion(BaseModel):
    PLAN_CHOICES = (
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('elite', 'Elite'),
    )
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='promotions')
    broker = models.ForeignKey(BrokerProfile, on_delete=models.CASCADE, related_name='promotions')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES)
    price = models.IntegerField()
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    payment_ref = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Promotion for {self.property.title}"


class Lead(BaseModel):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold'),
        ('converted', 'Converted'),
    )
    SOURCE_CHOICES = (
        ('ai_match', 'AI Match'),
        ('search', 'Search'),
        ('direct', 'Direct'),
        ('referral', 'Referral'),
    )
    broker = models.ForeignKey(BrokerProfile, on_delete=models.CASCADE, related_name='leads')
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='leads')
    buyer_name = models.CharField(max_length=120)
    buyer_phone = models.CharField(max_length=20)
    buyer_email = models.EmailField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=15, choices=SOURCE_CHOICES)

    def __str__(self):
        return f"Lead {self.buyer_name} for {self.property.title}"
