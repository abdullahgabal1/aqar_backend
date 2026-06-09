import random
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

def send_response(data=None, status=200, message='Success'):
    """Uniform API response envelope."""
    return Response({
        'success': True if 200 <= status < 300 else False,
        'message': message,
        'data': data,
        'errors': None
    }, status=status)
