from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Property, PropertyImage, Favorite, VisitRequest


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_primary', 'order']


class PropertyListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    broker_name = serializers.CharField(source='broker.company_name', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'price', 'area', 'bedrooms', 'bathrooms',
            'city', 'area_name', 'status', 'primary_image', 'broker_name',
            'is_featured', 'created_at',
        ]

    @extend_schema_field(serializers.URLField(allow_null=True))
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

    @extend_schema_field(serializers.DictField())
    def get_broker_info(self, obj):
        """
        Returns broker info. Phone is only included for authenticated users.
        """
        request = self.context.get('request')
        info = {
            'id': str(obj.broker.id),
            'name': obj.broker.company_name,
            'rating': float(obj.broker.rating),
        }
        # Only expose phone to authenticated users
        if request and request.user and request.user.is_authenticated:
            info['phone'] = obj.broker.user.phone
        return info


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
        fields = [
            'id', 'property', 'property_title', 'visit_date',
            'visit_time', 'visit_type', 'status', 'notes', 'created_at',
        ]
        read_only_fields = ['status', 'created_at']
