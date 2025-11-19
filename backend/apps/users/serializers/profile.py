"""
User Profile serializers
"""
from rest_framework import serializers
from apps.users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User Profile serializer
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'user_email',
            'phone',
            'avatar',
            'bio',
            'address',
            'city',
            'country',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'user_email', 'created_at', 'updated_at']
