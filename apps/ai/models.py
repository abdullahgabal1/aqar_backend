from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel

User = get_user_model()

class MatchScore(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_scores')
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='match_scores')
    score = models.SmallIntegerField()
    factors = models.JSONField(null=True, blank=True)
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"Score: {self.score} for {self.user.email} -> {self.property.title}"


class AIConversation(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    messages = models.JSONField(default=list)
    context_property = models.ForeignKey('properties.Property', on_delete=models.SET_NULL, null=True, blank=True)
    suggested_property_ids = models.JSONField(default=list)

    def __str__(self):
        return f"Chat Session {self.id} for {self.user.email}"


class AIPropertySuggestion(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_suggestions')
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='property_suggestions')
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='ai_suggestions')
    
    suggested_in_message = models.IntegerField()
    suggestion_reason = models.TextField()
    match_score = models.SmallIntegerField()
    
    was_clicked = models.BooleanField(default=False)
    was_saved = models.BooleanField(default=False)
    was_visited = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    saved_at = models.DateTimeField(null=True, blank=True)
    visited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'conversation', 'property')
        ordering = ['-created_at']

    def __str__(self):
        return f"Suggestion: {self.property.title} to {self.user.email}"
