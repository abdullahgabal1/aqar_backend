from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class OTPRateThrottle(AnonRateThrottle):
    """
    Strict per-IP rate limit for OTP endpoints (register, verify).
    5 attempts per 15 minutes to prevent brute-force on 6-digit OTPs.
    """
    rate = '5/15min'
    scope = 'otp'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident,
        }
