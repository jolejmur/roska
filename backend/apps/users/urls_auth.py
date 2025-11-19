"""
Authentication URLs
"""
from django.urls import path
from apps.users.views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    PasswordResetView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('forgot-password/', PasswordResetView.as_view(), name='forgot-password'),
]
