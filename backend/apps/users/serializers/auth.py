"""
Authentication serializers
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(serializers.Serializer):
    """
    Login serializer.
    Compatible with FastAPI JWT login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Authenticate using email instead of username
            user = authenticate(request=self.context.get('request'),
                              username=email, password=password)

            if not user:
                raise serializers.ValidationError('Credenciales inválidas')

            if not user.is_active:
                raise serializers.ValidationError('Usuario desactivado')

        else:
            raise serializers.ValidationError('Debe incluir email y password')

        attrs['user'] = user
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer to use email instead of username
    """
    username_field = 'email'


class RegisterSerializer(serializers.Serializer):
    """
    Register serializer (for future use if registration is enabled).
    Currently, users must be created by admin.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        """Check if email is already registered"""
        from apps.users.models import User
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este email ya está registrado')
        return value


class TokenSerializer(serializers.Serializer):
    """
    Token response serializer.
    Compatible with FastAPI JWT response.
    """
    access = serializers.CharField()
    refresh = serializers.CharField()
    token_type = serializers.CharField(default='bearer')
