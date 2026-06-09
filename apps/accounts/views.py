from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserProfileSerializer, UserPreferencesSerializer, VerifyOTPSerializer
from .services import send_otp_email, verify_otp_code, generate_jwt_tokens, get_or_create_preferences

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            get_or_create_preferences(user)
            send_otp_email(user)
            
            tokens = generate_jwt_tokens(user)
            user_data = UserProfileSerializer(user).data
            
            return Response({
                'success': True,
                'message': 'User registered successfully. OTP sent.',
                'data': {'user': user_data, 'tokens': tokens},
                'errors': None
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'message': 'Validation error', 'data': None, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            is_valid = verify_otp_code(request.user, serializer.validated_data['otp'], serializer.validated_data['channel'])
            if is_valid:
                return Response({'success': True, 'message': 'Account verified.', 'data': {'verified': True}, 'errors': None})
            return Response({'success': False, 'message': 'Invalid or expired OTP.', 'data': None, 'errors': {}}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': False, 'message': 'Validation error', 'data': None, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({'success': True, 'message': 'Profile retrieved.', 'data': serializer.data, 'errors': None})

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Profile updated.', 'data': serializer.data, 'errors': None})
        return Response({'success': False, 'message': 'Validation error', 'data': None, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class PreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        prefs = get_or_create_preferences(request.user)
        serializer = UserPreferencesSerializer(prefs, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Preferences updated.', 'data': serializer.data, 'errors': None})
        return Response({'success': False, 'message': 'Validation error', 'data': None, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'success': True, 'message': 'Logged out successfully.', 'data': None, 'errors': None}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'success': False, 'message': 'Invalid token.', 'data': None, 'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)
