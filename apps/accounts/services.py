from django.core.cache import cache
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from core.utils import generate_otp
# import sendgrid
# import sendgrid.helpers.mail as sg_mail

def send_otp_email(user):
    otp = generate_otp(6)
    cache_key = f"otp_email_{user.id}"
    cache.set(cache_key, otp, timeout=600)  # 10 min TTL
    
    # Mock sending email
    print(f"Mock: Sent OTP {otp} to {user.email}")
    # In production:
    # sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    # message = sg_mail.Mail(
    #     from_email='noreply@aqar.ai',
    #     to_emails=user.email,
    #     subject='Your AQAR AI Verification Code',
    #     html_content=f'<strong>{otp}</strong> is your code. Valid for 10 minutes.'
    # )
    # sg.send(message)

def send_otp_sms(user):
    otp = generate_otp(6)
    cache_key = f"otp_phone_{user.id}"
    cache.set(cache_key, otp, timeout=600)  # 10 min TTL
    
    print(f"Mock: Sent OTP {otp} to {user.phone}")

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
