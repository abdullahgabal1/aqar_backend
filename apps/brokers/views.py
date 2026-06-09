from rest_framework import viewsets, permissions
from .models import BrokerProfile, Lead
from .serializers import BrokerProfileSerializer, LeadSerializer
from core.permissions import IsBroker

class BrokerProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BrokerProfileSerializer

    def get_queryset(self):
        return BrokerProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LeadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsBroker]
    serializer_class = LeadSerializer

    def get_queryset(self):
        broker = BrokerProfile.objects.filter(user=self.request.user).first()
        if broker:
            return Lead.objects.filter(broker=broker)
        return Lead.objects.none()
