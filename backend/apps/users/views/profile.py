"""
User Profile views
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.users.models import UserProfile
from apps.users.serializers import UserProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Gestión de Perfiles de Usuario

    Endpoints para administrar perfiles extendidos de usuarios.
    Cada usuario solo puede ver y editar su propio perfil.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Users']

    def get_queryset(self):
        """Users can only see their own profile"""
        # Skip permission checks during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return UserProfile.objects.none()

        return UserProfile.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        tags=['Perfiles'],
        operation_description="Listar perfiles de usuario. Cada usuario solo puede ver su propio perfil.",
        responses={
            200: UserProfileSerializer(many=True),
            401: "No autenticado"
        }
    )
    def list(self, request, *args, **kwargs):
        """GET /api/profiles/ - List user profiles"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Perfiles'],
        operation_description="Obtener detalles del perfil de un usuario.",
        responses={
            200: UserProfileSerializer(),
            401: "No autenticado",
            403: "Sin permiso",
            404: "Perfil no encontrado"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """GET /api/profiles/{id}/ - Get profile details"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Perfiles'],
        operation_description="Crear perfil para el usuario actual si no existe.",
        responses={
            201: UserProfileSerializer(),
            400: "El perfil ya existe",
            401: "No autenticado"
        }
    )
    def create(self, request, *args, **kwargs):
        """Create profile for current user if it doesn't exist"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if not created:
            return Response({
                'detail': 'El perfil ya existe'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=['Perfiles'],
        operation_description="Actualizar el perfil del usuario actual.",
        request_body=UserProfileSerializer,
        responses={
            200: UserProfileSerializer(),
            400: "Datos inválidos",
            401: "No autenticado"
        }
    )
    def update(self, request, *args, **kwargs):
        """Update current user profile"""
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(profile, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Perfiles'],
        operation_description="Actualización parcial del perfil del usuario actual.",
        request_body=UserProfileSerializer,
        responses={
            200: UserProfileSerializer(),
            400: "Datos inválidos",
            401: "No autenticado"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/profiles/{id}/ - Partial update profile"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Perfiles'],
        operation_description="Eliminar el perfil del usuario actual.",
        responses={
            204: "Perfil eliminado exitosamente",
            401: "No autenticado",
            404: "Perfil no encontrado"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """DELETE /api/profiles/{id}/ - Delete profile"""
        return super().destroy(request, *args, **kwargs)
