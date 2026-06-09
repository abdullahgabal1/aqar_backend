from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrokerProfileViewSet, LeadViewSet

router = DefaultRouter()
router.register(r'profile', BrokerProfileViewSet, basename='broker_profile')
router.register(r'leads', LeadViewSet, basename='lead')

urlpatterns = [
    path('', include(router.urls)),
]
