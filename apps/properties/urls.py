from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, FavoriteViewSet, VisitRequestViewSet

router = DefaultRouter()
router.register(r'listings', PropertyViewSet, basename='property')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'visits', VisitRequestViewSet, basename='visit')

urlpatterns = [
    path('', include(router.urls)),
]
