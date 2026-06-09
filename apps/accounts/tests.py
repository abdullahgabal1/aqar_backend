import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status

User = get_user_model()


# ──────────────────────────────────────────────────────────
# Registration Tests
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRegistration:

    def test_register_success(self, api_client):
        payload = {
            'email': 'new@aqar.ai',
            'full_name': 'New User',
            'password': 'SecurePass123!',
        }
        resp = api_client.post('/api/v1/auth/register/', payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['success'] is True
        assert 'tokens' in resp.data['data']
        assert resp.data['data']['user']['role'] == 'user'

    def test_register_duplicate_email(self, api_client, create_user):
        create_user(email='dup@aqar.ai')
        payload = {
            'email': 'dup@aqar.ai',
            'full_name': 'Dup',
            'password': 'SecurePass123!',
        }
        resp = api_client.post('/api/v1/auth/register/', payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_cannot_set_admin_role(self, api_client):
        """🔴 CRITICAL: Users must NOT be able to self-assign admin role."""
        payload = {
            'email': 'hacker@aqar.ai',
            'full_name': 'Hacker',
            'password': 'SecurePass123!',
            'role': 'admin',
        }
        resp = api_client.post('/api/v1/auth/register/', payload, format='json')
        # Even if 'role' is sent, it must be ignored — user should be 'user'
        if resp.status_code == status.HTTP_201_CREATED:
            assert resp.data['data']['user']['role'] == 'user'
        # Verify in DB
        user = User.objects.filter(email='hacker@aqar.ai').first()
        if user:
            assert user.role == 'user'

    def test_register_cannot_set_broker_role(self, api_client):
        """Users must NOT be able to self-assign broker role."""
        payload = {
            'email': 'fake_broker@aqar.ai',
            'full_name': 'Fake Broker',
            'password': 'SecurePass123!',
            'role': 'broker',
        }
        resp = api_client.post('/api/v1/auth/register/', payload, format='json')
        if resp.status_code == status.HTTP_201_CREATED:
            assert resp.data['data']['user']['role'] == 'user'

    def test_register_weak_password_rejected(self, api_client):
        payload = {
            'email': 'weak@aqar.ai',
            'full_name': 'Weak',
            'password': '123',
        }
        resp = api_client.post('/api/v1/auth/register/', payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ──────────────────────────────────────────────────────────
# OTP Verification Tests
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestOTPVerification:

    def test_verify_valid_otp(self, auth_client):
        client, user = auth_client
        # Manually set OTP in cache
        cache.set(f'otp_email_{user.id}', '123456', timeout=600)

        resp = client.post('/api/v1/auth/verify-otp/', {
            'otp': '123456',
            'channel': 'email',
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['success'] is True

        user.refresh_from_db()
        assert user.is_verified is True

    def test_verify_wrong_otp(self, auth_client):
        client, user = auth_client
        cache.set(f'otp_email_{user.id}', '123456', timeout=600)

        resp = client.post('/api/v1/auth/verify-otp/', {
            'otp': '000000',
            'channel': 'email',
        }, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        user.refresh_from_db()
        assert user.is_verified is False

    def test_verify_expired_otp(self, auth_client):
        client, user = auth_client
        # Don't set any OTP in cache — simulates expiration

        resp = client.post('/api/v1/auth/verify-otp/', {
            'otp': '123456',
            'channel': 'email',
        }, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_otp_consumed_after_use(self, auth_client):
        client, user = auth_client
        cache.set(f'otp_email_{user.id}', '111111', timeout=600)

        # First attempt: success
        resp = client.post('/api/v1/auth/verify-otp/', {
            'otp': '111111',
            'channel': 'email',
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK

        # Second attempt with same OTP: should fail
        resp = client.post('/api/v1/auth/verify-otp/', {
            'otp': '111111',
            'channel': 'email',
        }, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ──────────────────────────────────────────────────────────
# Profile & Preferences Tests
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestProfile:

    def test_get_profile_authenticated(self, auth_client):
        client, user = auth_client
        resp = client.get('/api/v1/auth/profile/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['data']['email'] == user.email

    def test_get_profile_unauthenticated(self, api_client):
        resp = api_client.get('/api/v1/auth/profile/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_name(self, auth_client):
        client, user = auth_client
        resp = client.patch('/api/v1/auth/profile/', {
            'full_name': 'Updated Name',
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.full_name == 'Updated Name'

    def test_cannot_change_role_via_profile(self, auth_client):
        """Users must not be able to escalate privileges via profile update."""
        client, user = auth_client
        resp = client.patch('/api/v1/auth/profile/', {
            'role': 'admin',
        }, format='json')
        user.refresh_from_db()
        assert user.role == 'user'


# ──────────────────────────────────────────────────────────
# Logout Tests
# ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestLogout:

    def test_logout_success(self, auth_client):
        client, user = auth_client
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        resp = client.post('/api/v1/auth/logout/', {
            'refresh': str(refresh),
        }, format='json')
        assert resp.status_code == status.HTTP_205_RESET_CONTENT

    def test_logout_without_token(self, auth_client):
        client, user = auth_client
        resp = client.post('/api/v1/auth/logout/', {}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
