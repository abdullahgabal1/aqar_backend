from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel

User = get_user_model()

class Notification(BaseModel):
    TYPE_CHOICES = (
        ('new_match', 'New Match'),
        ('visit_confirmed', 'Visit Confirmed'),
        ('new_lead', 'New Lead'),
        ('price_drop', 'Price Drop'),
        ('message', 'Message'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=120)
    body = models.TextField()
    data = models.JSONField(null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type} to {self.user.email}"
