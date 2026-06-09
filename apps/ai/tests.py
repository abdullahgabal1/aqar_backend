import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from ai.models import AIConversation, AIPropertySuggestion
from properties.models import Property
from brokers.models import BrokerProfile

User = get_user_model()


@pytest.fixture
def ai_property(broker_user):
    user, profile = broker_user
    return Property.objects.create(
        broker=profile,
        title='AI Test Property',
        property_type='apartment',
        status='active',
        price=3000000,
        area=150,
        bedrooms=3,
        bathrooms=2,
        city='Cairo',
        area_name='Zamalek',
        finishing='lux',
    )


# ──────────────────────────────────────────────────────────
# AI Chat Tests
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAIChat:

    def test_chat_creates_conversation(self, auth_client, ai_property):
        client, user = auth_client
        resp = client.post('/api/v1/ai/chat/', {
            'message': 'Find me a 3 bedroom apartment in Cairo',
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['success'] is True
        assert 'conversation_id' in resp.data['data']

    def test_chat_requires_message(self, auth_client):
        client, user = auth_client
        resp = client.post('/api/v1/ai/chat/', {}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_chat_invalid_conversation_id_returns_404(self, auth_client):
        """🔴 CRITICAL: Must not return 500 on bad conversation ID."""
        client, user = auth_client
        import uuid
        resp = client.post('/api/v1/ai/chat/', {
            'message': 'Hello',
            'conversation_id': str(uuid.uuid4()),
        }, format='json')
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_chat_unauthenticated_rejected(self, api_client):
        resp = api_client.post('/api/v1/ai/chat/', {
            'message': 'Hello',
        }, format='json')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_duplicate_suggestions_no_crash(self, auth_client, ai_property):
        """🟠 MEDIUM: Sending two messages in same conversation must not IntegrityError."""
        client, user = auth_client
        # First message
        resp1 = client.post('/api/v1/ai/chat/', {
            'message': 'First message',
        }, format='json')
        assert resp1.status_code == status.HTTP_200_OK
        conv_id = resp1.data['data']['conversation_id']

        # Second message to same conversation
        resp2 = client.post('/api/v1/ai/chat/', {
            'message': 'Second message',
            'conversation_id': conv_id,
        }, format='json')
        assert resp2.status_code == status.HTTP_200_OK


# ──────────────────────────────────────────────────────────
# Suggestion Tracking Tests
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSuggestionTracking:

    def test_track_click(self, auth_client, ai_property):
        client, user = auth_client
        conv = AIConversation.objects.create(user=user)
        suggestion = AIPropertySuggestion.objects.create(
            user=user,
            conversation=conv,
            property=ai_property,
            suggested_in_message=0,
            suggestion_reason='Test',
            match_score=80,
        )
        resp = client.post(f'/api/v1/ai/suggestions/{suggestion.id}/track/', {
            'action': 'click',
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        suggestion.refresh_from_db()
        assert suggestion.was_clicked is True

    def test_track_invalid_suggestion_returns_404(self, auth_client):
        client, user = auth_client
        import uuid
        resp = client.post(f'/api/v1/ai/suggestions/{uuid.uuid4()}/track/', {
            'action': 'click',
        }, format='json')
        assert resp.status_code == status.HTTP_404_NOT_FOUND
