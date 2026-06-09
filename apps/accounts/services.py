import logging
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from core.utils import generate_otp

logger = logging.getLogger(__name__)


def send_otp_email(user):
    """Generate and send OTP via email. Uses Django email backend (console in dev, SMTP in prod)."""
    otp = generate_otp(6)
    cache_key = f"otp_email_{user.id}"
    cache.set(cache_key, otp, timeout=600)  # 10 min TTL

    # Reset failed attempts counter
    attempts_key = f"otp_attempts_email_{user.id}"
    cache.delete(attempts_key)

    subject = 'Your AQAR AI Verification Code'
    message = f'{otp} is your verification code. Valid for 10 minutes.'
    html_message = f'<strong>{otp}</strong> is your verification code. Valid for 10 minutes.'

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email='noreply@aqar.ai',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info("OTP email sent to user_id=%s", user.id)
    except Exception:
        logger.exception("Failed to send OTP email to user_id=%s", user.id)


def send_otp_sms(user):
    """Generate and send OTP via SMS. Placeholder — integrate Vonage/Twilio."""
    otp = generate_otp(6)
    cache_key = f"otp_phone_{user.id}"
    cache.set(cache_key, otp, timeout=600)  # 10 min TTL

    # Reset failed attempts counter
    attempts_key = f"otp_attempts_phone_{user.id}"
    cache.delete(attempts_key)

    # TODO: integrate Vonage / Twilio SDK here
    logger.info("OTP SMS queued for user_id=%s", user.id)


def verify_otp_code(user, code, channel):
    """
    Verify an OTP code with attempt limiting.
    
    Returns:
        tuple: (success: bool, reason: str)
               - (True, 'verified') on success
               - (False, 'invalid_code') on wrong code
               - (False, 'expired') on expired/not found OTP
               - (False, 'too_many_attempts') on exceeding attempt limit
    """
    if channel not in ['email', 'phone']:
        return False, 'invalid_channel'

    cache_key = f"otp_{channel}_{user.id}"
    attempts_key = f"otp_attempts_{channel}_{user.id}"
    
    # Get current attempt count (default 0 if not set)
    attempts = cache.get(attempts_key, 0)
    
    # Max 5 attempts per OTP (10 minute window)
    if attempts >= 5:
        logger.warning("OTP verification attempt limit exceeded for user_id=%s channel=%s", user.id, channel)
        return False, 'too_many_attempts'
    
    cached_otp = cache.get(cache_key)

    if cached_otp and str(cached_otp) == str(code):
        # Success: clear both cache entries
        cache.delete(cache_key)
        cache.delete(attempts_key)
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        logger.info("OTP verified successfully for user_id=%s channel=%s", user.id, channel)
        return True, 'verified'
    
    # Wrong code: increment attempt counter
    cache.set(attempts_key, attempts + 1, timeout=600)
    
    if not cached_otp:
        logger.warning("OTP expired or not found for user_id=%s channel=%s", user.id, channel)
        return False, 'expired'
    
    logger.warning("Invalid OTP attempt for user_id=%s channel=%s (attempt %d/5)", user.id, channel, attempts + 1)
    return False, 'invalid_code'


def generate_jwt_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def get_or_create_preferences(user):
    from accounts.models import UserPreferences
    prefs, created = UserPreferences.objects.get_or_create(user=user)
    return prefs
