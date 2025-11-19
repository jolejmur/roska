from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.permissions.models import Role, RoleAssignment
from apps.permissions.serializers import (
    RoleSerializer,
    RoleListSerializer,
    RoleCreateUpdateSerializer,
    RoleAssignmentSerializer
)


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Roles
    """
    queryset = Role.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for direct array response

    def get_queryset(self):
        """Filter queryset based on query params"""
        if getattr(self, 'swagger_fake_view', False):
            return Role.objects.none()

        queryset = Role.objects.all()

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Filter by system roles
        is_system = self.request.query_params.get('is_system')
        if is_system is not None:
            queryset = queryset.filter(is_system=is_system.lower() == 'true')

        return queryset.prefetch_related('functions').select_related('created_by')

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return RoleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RoleCreateUpdateSerializer
        return RoleSerializer

    def perform_create(self, serializer):
        """Set created_by when creating a role"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        tags=['Gestión de roles'],
        operation_description="Listar todos los roles del sistema",
        manual_parameters=[
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Filtrar por estado activo (true/false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'is_system',
                openapi.IN_QUERY,
                description="Filtrar por roles del sistema (true/false)",
                type=openapi.TYPE_BOOLEAN
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de roles'],
        operation_description="Obtener detalles de un rol específico"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de roles'],
        operation_description="Crear un nuevo rol",
        responses={
            201: RoleSerializer,
            400: "Datos inválidos"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de roles'],
        operation_description="Actualizar completamente un rol",
        responses={
            200: RoleSerializer,
            400: "Datos inválidos o rol del sistema",
            404: "Rol no encontrado"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de roles'],
        operation_description="Actualizar parcialmente un rol",
        responses={
            200: RoleSerializer,
            400: "Datos inválidos o rol del sistema",
            404: "Rol no encontrado"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de roles'],
        operation_description="Eliminar un rol",
        responses={
            204: "Rol eliminado exitosamente",
            400: "No se puede eliminar rol del sistema",
            404: "Rol no encontrado"
        }
    )
    def destroy(self, request, *args, **kwargs):
        role = self.get_object()

        if role.is_system:
            return Response(
                {'error': 'No se pueden eliminar roles del sistema'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de roles'],
        operation_description="Obtener usuarios asignados a un rol",
        responses={200: RoleAssignmentSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users assigned to this role"""
        role = self.get_object()
        assignments = role.role_assignments.filter(is_active=True).select_related('user', 'assigned_by')
        serializer = RoleAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class RoleAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing role assignments to users
    """
    queryset = RoleAssignment.objects.all()
    serializer_class = RoleAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset based on query params"""
        if getattr(self, 'swagger_fake_view', False):
            return RoleAssignment.objects.none()

        queryset = RoleAssignment.objects.all()

        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by role
        role_id = self.request.query_params.get('role_id')
        if role_id:
            queryset = queryset.filter(role_id=role_id)

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.select_related('user', 'role', 'assigned_by')

    def perform_create(self, serializer):
        """Set assigned_by when creating an assignment"""
        serializer.save(assigned_by=self.request.user)

    @swagger_auto_schema(
        tags=['Asignación de roles'],
        operation_description="Listar todas las asignaciones de roles",
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="Filtrar por ID de usuario",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'role_id',
                openapi.IN_QUERY,
                description="Filtrar por ID de rol",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Filtrar por estado activo (true/false)",
                type=openapi.TYPE_BOOLEAN
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Asignación de roles'],
        operation_description="Obtener detalles de una asignación de rol"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Asignación de roles'],
        operation_description="Crear una nueva asignación de rol a un usuario",
        responses={
            201: RoleAssignmentSerializer,
            400: "El usuario ya tiene este rol asignado"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Asignación de roles'],
        operation_description="Actualizar una asignación de rol",
        responses={
            200: RoleAssignmentSerializer,
            400: "Datos inválidos",
            404: "Asignación no encontrada"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Asignación de roles'],
        operation_description="Actualizar parcialmente una asignación de rol"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Asignación de roles'],
        operation_description="Eliminar (desactivar) una asignación de rol",
        responses={
            204: "Asignación eliminada exitosamente",
            404: "Asignación no encontrada"
        }
    )
    def destroy(self, request, *args, **kwargs):
        # Instead of deleting, deactivate the assignment
        assignment = self.get_object()
        assignment.is_active = False
        assignment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
