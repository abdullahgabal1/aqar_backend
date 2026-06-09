import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from properties.models import Property
from brokers.models import BrokerProfile

User = get_user_model()


@pytest.fixture
def sample_property(broker_user):
    """Create a sample property for testing."""
    user, broker_profile = broker_user
    return Property.objects.create(
        broker=broker_profile,
        title='Test Villa',
        description='A beautiful test villa.',
        property_type='villa',
        status='active',
        price=5000000,
        area=250,
        bedrooms=4,
        bathrooms=3,
        city='Cairo',
        area_name='New Cairo',
        finishing='super_lux',
    )


# ──────────────────────────────────────────────────────────
# Property Listing Tests
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestPropertyListing:

    def test_list_properties_unauthenticated(self, api_client, sample_property):
        resp = api_client.get('/api/v1/properties/listings/')
        assert resp.status_code == status.HTTP_200_OK

    def test_property_detail_increments_views(self, api_client, sample_property):
        initial_views = sample_property.views_count
        api_client.get(f'/api/v1/properties/listings/{sample_property.id}/')
        sample_property.refresh_from_db()
        assert sample_property.views_count == initial_views + 1

    def test_broker_phone_hidden_from_anonymous(self, api_client, sample_property):
        """🟠 Broker phone must NOT be exposed to unauthenticated users."""
        resp = api_client.get(f'/api/v1/properties/listings/{sample_property.id}/')
        assert resp.status_code == status.HTTP_200_OK
        broker_info = resp.data['data']['broker_info']
        assert 'phone' not in broker_info

    def test_broker_phone_visible_to_authenticated(self, auth_client, sample_property):
        client, user = auth_client
        resp = client.get(f'/api/v1/properties/listings/{sample_property.id}/')
        assert resp.status_code == status.HTTP_200_OK
        broker_info = resp.data['data']['broker_info']
        assert 'phone' in broker_info


# ──────────────────────────────────────────────────────────
# Permission Tests
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestPropertyPermissions:

    def test_regular_user_cannot_create_property(self, auth_client):
        """Regular users must not be able to create listings — only brokers."""
        client, user = auth_client
        payload = {
            'title': 'Hack Listing',
            'property_type': 'villa',
            'price': 1000000,
            'area': 100,
            'bedrooms': 2,
            'bathrooms': 1,
            'city': 'Cairo',
            'area_name': 'Maadi',
            'finishing': 'lux',
        }
        resp = client.post('/api/v1/properties/listings/', payload, format='json')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_broker_can_create_property(self, broker_client):
        client, user, profile = broker_client
        payload = {
            'broker': str(profile.id),
            'title': 'Broker Listing',
            'property_type': 'apartment',
            'price': 2000000,
            'area': 120,
            'bedrooms': 3,
            'bathrooms': 2,
            'city': 'Cairo',
            'area_name': '6th October',
            'finishing': 'super_lux',
            'status': 'active',
        }
        resp = client.post('/api/v1/properties/listings/', payload, format='json')
        assert resp.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]


# ──────────────────────────────────────────────────────────
# Soft-Delete Tests
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSoftDelete:

    def test_soft_deleted_property_hidden_from_list(self, api_client, sample_property):
        sample_property.delete()  # Soft delete
        resp = api_client.get('/api/v1/properties/listings/')
        assert resp.status_code == status.HTTP_200_OK
        ids = [p['id'] for p in resp.data['data']['results']]
        assert str(sample_property.id) not in ids

    def test_soft_deleted_property_hidden_from_favorites(self, auth_client, sample_property):
        from properties.models import Favorite
        client, user = auth_client
        # Create a favorite
        Favorite.objects.create(user=user, property=sample_property)
        # Soft-delete the property
        sample_property.delete()

        resp = client.get('/api/v1/properties/favorites/')
        assert resp.status_code == status.HTTP_200_OK
        # The favorite should not appear since the property is soft-deleted
        results = resp.data.get('data', {}).get('results', resp.data.get('results', []))
        assert len(results) == 0
