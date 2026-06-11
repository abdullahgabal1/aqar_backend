import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory fixture for creating users."""
    def _create_user(email='test@aqar.ai', password='TestPass123!', **kwargs):
        defaults = {
            'full_name': 'Test User',
            'role': 'user',
        }
        defaults.update(kwargs)
        user = User.objects.create_user(email=email, password=password, **defaults)
        return user
    return _create_user


@pytest.fixture
def auth_client(api_client, create_user):
    """Returns an authenticated APIClient with verified user."""
    user = create_user()
    # Verify user for tests that require IsVerified
    user.is_verified = True
    user.save(update_fields=['is_verified'])
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def broker_user(db):
    """Create a user with broker role and a BrokerProfile."""
    from brokers.models import BrokerProfile
    user = User.objects.create_user(
        email='broker@aqar.ai',
        password='BrokerPass123!',
        full_name='Test Broker',
        role='broker',
    )
    # Mark broker as verified for property creation tests
    user.is_verified = True
    user.save(update_fields=['is_verified'])
    broker_profile = BrokerProfile.objects.create(
        user=user,
        company_name='Test Realty',
        license_number='LIC-12345',
    )
    return user, broker_profile


@pytest.fixture
def broker_client(api_client, broker_user):
    """Returns an authenticated APIClient for a broker."""
    user, profile = broker_user
    api_client.force_authenticate(user=user)
    return api_client, user, profile


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the cache before each test."""
    cache.clear()
    yield
    cache.clear()
