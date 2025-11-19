"""
Permissions app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.permissions.views import RoleViewSet, RoleAssignmentViewSet

app_name = 'permissions'

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'role-assignments', RoleAssignmentViewSet, basename='role-assignment')

urlpatterns = [
    path('', include(router.urls)),
]
