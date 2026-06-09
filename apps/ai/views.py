import logging
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers

from .models import AIConversation, AIPropertySuggestion
from properties.models import Property
from core.utils import send_response
from core.permissions import IsVerified

logger = logging.getLogger(__name__)


class AIChatView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVerified]

    @extend_schema(
        request=inline_serializer(
            name='AIChatRequest',
            fields={
                'message': drf_serializers.CharField(),
                'conversation_id': drf_serializers.UUIDField(required=False),
            },
        ),
    )
    def post(self, request):
        user_message = request.data.get('message')
        if not user_message:
            return send_response(status=400, message='Message is required.')

        conversation_id = request.data.get('conversation_id')

        if conversation_id:
            conversation = get_object_or_404(
                AIConversation, id=conversation_id, user=request.user
            )
        else:
            conversation = AIConversation.objects.create(user=request.user)

        conversation.messages.append({'role': 'user', 'content': user_message})

        # Stub response — replace with real LLM call
        ai_response = "This is a stub AI response. We found some matching properties."
        suggested_pks = list(Property.objects.values_list('id', flat=True)[:2])

        conversation.messages.append({'role': 'assistant', 'content': ai_response})
        conversation.save()

        # Use get_or_create to prevent IntegrityError on duplicate suggestions
        created_suggestions = []
        for prop_id in suggested_pks:
            suggestion, created = AIPropertySuggestion.objects.get_or_create(
                user=request.user,
                conversation=conversation,
                property_id=prop_id,
                defaults={
                    'suggested_in_message': len(conversation.messages) - 1,
                    'suggestion_reason': "Matches your area preference.",
                    'match_score': 85,
                },
            )
            created_suggestions.append(str(suggestion.id))

        return send_response(
            data={
                'conversation_id': str(conversation.id),
                'reply': ai_response,
                'suggestions': created_suggestions,
            },
            message='AI replied.',
        )


class TrackSuggestionInteractionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name='TrackInteractionRequest',
            fields={'action': drf_serializers.ChoiceField(choices=['click', 'save', 'visit'])},
        ),
    )
    def post(self, request, suggestion_id):
        action_type = request.data.get('action')
        suggestion = get_object_or_404(
            AIPropertySuggestion, id=suggestion_id, user=request.user
        )

        now = timezone.now()
        update_fields = []

        if action_type == 'click':
            suggestion.was_clicked = True
            suggestion.clicked_at = now
            update_fields = ['was_clicked', 'clicked_at']
        elif action_type == 'save':
            suggestion.was_saved = True
            suggestion.saved_at = now
            update_fields = ['was_saved', 'saved_at']
        elif action_type == 'visit':
            suggestion.was_visited = True
            suggestion.visited_at = now
            update_fields = ['was_visited', 'visited_at']
        else:
            return send_response(status=400, message='Invalid action. Use click, save, or visit.')

        suggestion.save(update_fields=update_fields)
        return send_response(message='Tracked.')
