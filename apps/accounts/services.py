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

    # TODO: integrate Vonage / Twilio SDK here
    logger.info("OTP SMS queued for user_id=%s", user.id)


def verify_otp_code(user, code, channel):
    if channel not in ['email', 'phone']:
        return False

    cache_key = f"otp_{channel}_{user.id}"
    cached_otp = cache.get(cache_key)

    if cached_otp and str(cached_otp) == str(code):
        cache.delete(cache_key)
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        return True
    return False


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
