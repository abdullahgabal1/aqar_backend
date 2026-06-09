from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import F
from .models import Property, Favorite, VisitRequest
from .serializers import (
    PropertyListSerializer, PropertyDetailSerializer,
    FavoriteSerializer, VisitRequestSerializer,
)
from core.permissions import IsBroker
from core.utils import send_response


class PropertyViewSet(viewsets.ModelViewSet):
    # Fix N+1: select_related broker AND broker__user for get_broker_info()
    queryset = Property.objects.filter(
        status='active'
    ).select_related('broker', 'broker__user')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBroker()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        return PropertyDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Atomic increment of views_count
        Property.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return send_response(data=serializer.data, message='Property details.')


class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        # Fix soft-delete bypass: only include non-deleted properties via select_related
        return Favorite.objects.filter(
            user=self.request.user,
            property__is_deleted=False,
        ).select_related('property', 'property__broker')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VisitRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VisitRequestSerializer

    def get_queryset(self):
        # Fix soft-delete bypass: only include non-deleted properties
        return VisitRequest.objects.filter(
            user=self.request.user,
            property__is_deleted=False,
        ).select_related('property')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
