from rest_framework import serializers
from .models import Property, PropertyImage, Favorite, VisitRequest
from brokers.models import BrokerProfile

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_primary', 'order']

class PropertyListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    broker_name = serializers.CharField(source='broker.company_name', read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'title', 'price', 'area', 'bedrooms', 'bathrooms', 'city', 'area_name', 'status', 'primary_image', 'broker_name', 'is_featured', 'created_at']

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first()
        if img:
            return img.image.url
        return None

class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    broker_info = serializers.SerializerMethodField()

    class Meta:
        model = Property
        exclude = ['is_deleted', 'deleted_at']

    def get_broker_info(self, obj):
        return {
            'id': obj.broker.id,
            'name': obj.broker.company_name,
            'phone': obj.broker.user.phone,
            'rating': obj.broker.rating
        }

class FavoriteSerializer(serializers.ModelSerializer):
    property_details = PropertyListSerializer(source='property', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'property', 'property_details', 'source', 'created_at']
        read_only_fields = ['source', 'created_at']

class VisitRequestSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = VisitRequest
        fields = ['id', 'property', 'property_title', 'visit_date', 'visit_time', 'visit_type', 'status', 'notes', 'created_at']
        read_only_fields = ['status', 'created_at']
