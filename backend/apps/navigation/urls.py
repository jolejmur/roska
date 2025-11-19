"""
Navigation app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.navigation.views import FunctionViewSet, CategoryViewSet

app_name = 'navigation'

router = DefaultRouter()
router.register(r'functions', FunctionViewSet, basename='function')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]
