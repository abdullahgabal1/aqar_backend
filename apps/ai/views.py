from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import AIConversation, AIPropertySuggestion
from properties.models import Property
# Assume an ai_service module exists for contacting the LLM
# from .services import get_ai_response 

class AIChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message')
        conversation_id = request.data.get('conversation_id')
        
        if conversation_id:
            conversation = AIConversation.objects.get(id=conversation_id, user=request.user)
        else:
            conversation = AIConversation.objects.create(user=request.user)
        
        conversation.messages.append({'role': 'user', 'content': user_message})
        
        # Stub response
        ai_response = "This is a stub AI response. We found some matching properties."
        suggested_pks = list(Property.objects.values_list('id', flat=True)[:2])
        
        conversation.messages.append({'role': 'assistant', 'content': ai_response})
        conversation.save()
        
        for prop_id in suggested_pks:
            AIPropertySuggestion.objects.create(
                user=request.user,
                conversation=conversation,
                property_id=prop_id,
                suggested_in_message=len(conversation.messages) - 1,
                suggestion_reason="Matches your area preference.",
                match_score=85
            )

        return Response({
            'success': True,
            'message': 'AI replied.',
            'data': {
                'conversation_id': conversation.id,
                'reply': ai_response,
                'suggestions': suggested_pks
            },
            'errors': None
        })

class TrackSuggestionInteractionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, suggestion_id):
        action = request.data.get('action') # 'click', 'save', 'visit'
        try:
            suggestion = AIPropertySuggestion.objects.get(id=suggestion_id, user=request.user)
            if action == 'click':
                suggestion.was_clicked = True
            elif action == 'save':
                suggestion.was_saved = True
            elif action == 'visit':
                suggestion.was_visited = True
            suggestion.save()
            return Response({'success': True, 'message': 'Tracked.'})
        except AIPropertySuggestion.DoesNotExist:
            return Response({'success': False, 'message': 'Not found.'}, status=404)
