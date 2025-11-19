"""
Users app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet, ProfileViewSet

# Router for ViewSets
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
