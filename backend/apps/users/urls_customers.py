"""
Customers app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import CustomerViewSet

# Router for ViewSets
router = DefaultRouter()
router.register(r'', CustomerViewSet, basename='customer')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
