from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from .serializers import RegisterSerializer, UserProfileSerializer, UserPreferencesSerializer, VerifyOTPSerializer
from .services import send_otp_email, verify_otp_code, generate_jwt_tokens, get_or_create_preferences
from core.utils import send_response
from core.throttles import OTPRateThrottle

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OTPRateThrottle]

    @extend_schema(request=RegisterSerializer, responses={201: UserProfileSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            get_or_create_preferences(user)
            send_otp_email(user)

            tokens = generate_jwt_tokens(user)
            user_data = UserProfileSerializer(user).data

            return send_response(
                data={'user': user_data, 'tokens': tokens},
                status=201,
                message='User registered successfully. OTP sent.',
            )
        return send_response(data=None, status=400, message='Validation error')


class VerifyOTPView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [OTPRateThrottle]

    @extend_schema(request=VerifyOTPSerializer)
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            is_valid, reason = verify_otp_code(
                request.user,
                serializer.validated_data['otp'],
                serializer.validated_data['channel'],
            )
            if is_valid:
                return send_response(data={'verified': True}, message='Account verified.')
            
            # Return appropriate error message based on failure reason
            error_messages = {
                'invalid_code': 'Invalid OTP code. Please try again.',
                'expired': 'OTP has expired. Please request a new one.',
                'too_many_attempts': 'Too many failed attempts. Please request a new OTP.',
                'invalid_channel': 'Invalid channel.',
            }
            message = error_messages.get(reason, 'Verification failed.')
            return send_response(status=400, message=message)
        return send_response(status=400, message='Validation error')


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserProfileSerializer})
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return send_response(data=serializer.data, message='Profile retrieved.')

    @extend_schema(request=UserProfileSerializer, responses={200: UserProfileSerializer})
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return send_response(data=serializer.data, message='Profile updated.')
        return send_response(status=400, message='Validation error')


class PreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UserPreferencesSerializer, responses={200: UserPreferencesSerializer})
    def put(self, request):
        prefs = get_or_create_preferences(request.user)
        serializer = UserPreferencesSerializer(prefs, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return send_response(data=serializer.data, message='Preferences updated.')
        return send_response(status=400, message='Validation error')


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return send_response(status=400, message='Refresh token is required.')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return send_response(status=205, message='Logged out successfully.')
        except Exception:
            return send_response(status=400, message='Invalid token.')
