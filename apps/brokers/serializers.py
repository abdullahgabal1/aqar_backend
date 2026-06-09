from rest_framework import serializers
from .models import BrokerProfile, Lead

class BrokerProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = BrokerProfile
        fields = ['id', 'user_email', 'company_name', 'license_number', 'is_verified', 'rating', 'total_leads', 'subscription_plan']
        read_only_fields = ['is_verified', 'rating', 'total_leads', 'subscription_plan']

class LeadSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    
    class Meta:
        model = Lead
        fields = ['id', 'property', 'property_title', 'buyer_name', 'buyer_phone', 'buyer_email', 'status', 'notes', 'source', 'created_at']
        read_only_fields = ['source', 'created_at']
