from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from accounts.models import UserPreferences
from core.utils import egypt_phone_normalize

User = get_user_model()


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        exclude = ['user', 'created_at', 'updated_at', 'is_deleted', 'deleted_at']


class UserProfileSerializer(serializers.ModelSerializer):
    preferences = UserPreferencesSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone', 'role', 'avatar', 'is_verified', 'preferences']
        read_only_fields = ['id', 'email', 'role', 'is_verified']

    def validate_phone(self, value):
        return egypt_phone_normalize(value)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone', 'password']
        # NOTE: 'role' is intentionally excluded — all registrations default to 'user'.
        # Admin/Broker roles must be assigned via admin panel or internal API.

    def validate_phone(self, value):
        return egypt_phone_normalize(value)

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone=validated_data.get('phone'),
            password=validated_data['password'],
            role='user',  # Always force 'user' role on self-registration
        )
        return user


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, min_length=6)
    channel = serializers.ChoiceField(choices=['email', 'phone'])
