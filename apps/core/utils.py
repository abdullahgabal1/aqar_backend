import re
from rest_framework.response import Response


def generate_otp(length=6):
    """Generate a cryptographically secure numeric OTP."""
    import secrets
    return ''.join(str(secrets.choice(range(10))) for _ in range(length))


def egypt_phone_normalize(phone):
    """Normalize phone to +20xxxxxxxxxx"""
    if not phone:
        return phone
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('01'):
        return f'+20{phone[1:]}'
    elif phone.startswith('201'):
        return f'+{phone}'
    return f'+{phone}'


def send_response(data=None, status=200, message='Success', errors=None):
    """
    Uniform API response envelope used across all views.
    Automatically determines 'success' from the HTTP status code.
    """
    return Response({
        'success': 200 <= status < 300,
        'message': message,
        'data': data,
        'errors': errors,
    }, status=status)
