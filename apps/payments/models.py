from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel

User = get_user_model()

class Payment(BaseModel):
    GATEWAY_CHOICES = (
        ('stripe', 'Stripe'),
        ('fawry', 'Fawry'),
        ('vodafone_cash', 'Vodafone Cash'),
        ('bank', 'Bank Transfer'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    PAYMENT_TYPE_CHOICES = (
        ('lead_purchase', 'Lead Purchase'),
        ('promotion', 'Promotion'),
        ('subscription', 'Subscription'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.IntegerField()  # in piasters (x100)
    currency = models.CharField(max_length=3, default='EGP')
    gateway = models.CharField(max_length=15, choices=GATEWAY_CHOICES)
    gateway_ref = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    related_object_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.payment_type} - {self.amount/100} {self.currency}"


class BrokerSubscription(BaseModel):
    BILLING_CYCLES = (
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    )
    broker = models.ForeignKey('brokers.BrokerProfile', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=10)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLES)
    amount = models.IntegerField()
    started_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    auto_renew = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.plan} for {self.broker.company_name}"
