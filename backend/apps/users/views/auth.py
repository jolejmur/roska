"""
Authentication views
Migrated from FastAPI auth endpoints
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.users.serializers import LoginSerializer, CustomTokenObtainPairSerializer
from apps.users.models import User


class LoginView(TokenObtainPairView):
    """
    Iniciar Sesión

    Endpoint de autenticación con JWT tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    swagger_tags = ['Authentication']

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description="Login con email y contraseña. Retorna tokens JWT.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login exitoso",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "email": "admin@example.com",
                            "username": "admin",
                            "is_superuser": True
                        }
                    }
                }
            ),
            400: "Credenciales inválidas"
        }
    )
    def post(self, request, *args, **kwargs):
        """
        POST /api/auth/login
        Returns access and refresh tokens
        """
        # Validate credentials
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        # Generate full name
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'token_type': 'bearer',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': full_name,
                'is_superuser': user.is_superuser,
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Cerrar Sesión

    Invalida el refresh token actual agregándolo a la lista negra.
    """
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Authentication']

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description="Cierra la sesión actual invalidando el refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            }
        ),
        responses={
            200: "Sesión cerrada exitosamente",
            400: "Error al cerrar sesión"
        }
    )
    def post(self, request):
        """
        POST /api/auth/logout
        Blacklists the refresh token
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({
                'detail': 'Sesión cerrada exitosamente'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'detail': 'Error al cerrar sesión'
            }, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    """
    Refrescar Token de Acceso

    Genera un nuevo access token utilizando un refresh token válido.
    """
    permission_classes = [AllowAny]
    swagger_tags = ['Authentication']

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description="Genera un nuevo access token usando un refresh token válido.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            }
        ),
        responses={
            200: openapi.Response(
                description="Nuevo access token generado",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "token_type": "bearer"
                    }
                }
            ),
            400: "Refresh token requerido",
            401: "Refresh token inválido"
        }
    )
    def post(self, request):
        """
        POST /api/auth/refresh
        Returns new access token
        """
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'detail': 'Refresh token requerido'
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            return Response({
                'access': str(token.access_token),
                'token_type': 'bearer'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'detail': 'Refresh token inválido'
            }, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetView(APIView):
    """
    Recuperar Contraseña

    Solicita un email para restablecer la contraseña.
    """
    permission_classes = [AllowAny]
    swagger_tags = ['Authentication']

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description="Envía un email con instrucciones para restablecer la contraseña.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='Email del usuario')
            }
        ),
        responses={
            200: "Email enviado con instrucciones",
            400: "Email requerido"
        }
    )
    def post(self, request):
        """
        POST /api/auth/forgot-password
        Sends password reset email
        """
        email = request.data.get('email')

        if not email:
            return Response({
                'detail': 'Email requerido'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            # TODO: Implement password reset email logic
            # For now, just return success

            return Response({
                'detail': 'Se ha enviado un email con instrucciones para restablecer la contraseña'
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({
                'detail': 'Se ha enviado un email con instrucciones para restablecer la contraseña'
            }, status=status.HTTP_200_OK)
