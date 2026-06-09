from django.urls import path
from .views import AIChatView, TrackSuggestionInteractionView

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='ai_chat'),
    path('suggestions/<uuid:suggestion_id>/track/', TrackSuggestionInteractionView.as_view(), name='track_suggestion'),
]
