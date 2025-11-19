from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.navigation.models import Function
from apps.navigation.serializers import (
    FunctionSerializer,
    FunctionListSerializer,
    FunctionCreateUpdateSerializer
)


class FunctionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Functions (menu items)
    """
    queryset = Function.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination

    def get_queryset(self):
        """Filter queryset based on query params"""
        if getattr(self, 'swagger_fake_view', False):
            return Function.objects.none()

        queryset = Function.objects.all()

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Filter by parent (get root items or children of a parent)
        parent_id = self.request.query_params.get('parent_id')
        if parent_id is not None:
            if parent_id == 'null' or parent_id == '':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)

        return queryset.select_related('parent').order_by('order', 'name')

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return FunctionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FunctionCreateUpdateSerializer
        return FunctionSerializer

    @swagger_auto_schema(
        tags=['Gestión de funciones'],
        operation_description="Listar todas las funciones del sistema",
        manual_parameters=[
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Filtrar por estado activo (true/false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'parent_id',
                openapi.IN_QUERY,
                description="Filtrar por función padre (null para raíz)",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de funciones'],
        operation_description="Obtener detalles de una función específica"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de funciones'],
        operation_description="Crear una nueva función del sistema",
        responses={
            201: FunctionSerializer,
            400: "Datos inválidos",
            403: "Sin permiso"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new function.
        Requires Cerbos permission: function:create
        """
        from apps.permissions.services.cerbos_client import cerbos_service

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='function',
            resource_id='new',
            action='create'
        ):
            return Response({
                'detail': 'No tienes permiso para crear funciones.'
            }, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de funciones'],
        operation_description="Actualizar completamente una función",
        responses={
            200: FunctionSerializer,
            400: "Datos inválidos",
            403: "Sin permiso",
            404: "Función no encontrada"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        Update a function.
        Requires Cerbos permission: function:update
        """
        from apps.permissions.services.cerbos_client import cerbos_service

        instance = self.get_object()

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='function',
            resource_id=str(instance.id),
            action='update'
        ):
            return Response({
                'detail': 'No tienes permiso para actualizar funciones.'
            }, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de funciones'],
        operation_description="Actualizar parcialmente una función",
        responses={
            200: FunctionSerializer,
            400: "Datos inválidos",
            404: "Función no encontrada"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de funciones'],
        operation_description="Eliminar una función",
        responses={
            204: "Función eliminada exitosamente",
            403: "No se pueden eliminar funciones del sistema",
            404: "Función no encontrada"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete a function.
        System functions cannot be deleted.
        Requires Cerbos permission: function:delete
        """
        from apps.permissions.services.cerbos_client import cerbos_service

        instance = self.get_object()

        # Prevent deletion of system functions
        if instance.is_system:
            return Response({
                'detail': 'No se pueden eliminar funciones del sistema.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='function',
            resource_id=str(instance.id),
            action='delete'
        ):
            return Response({
                'detail': 'No tienes permiso para eliminar funciones.'
            }, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de funciones'],
        operation_description="Obtener árbol completo de funciones organizadas jerárquicamente",
        responses={200: FunctionSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Get complete function tree (only root functions with nested children)
        """
        root_functions = Function.objects.filter(
            parent__isnull=True,
            is_active=True
        ).order_by('order', 'name')

        serializer = FunctionSerializer(root_functions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Gestión de funciones'],
        operation_description="Reordenar funciones",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'functions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'order': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            }
        ),
        responses={
            200: "Funciones reordenadas exitosamente",
            400: "Datos inválidos"
        }
    )
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        Reorder functions by updating their order field
        Expects: { "functions": [{"id": 1, "order": 0}, {"id": 2, "order": 1}, ...] }
        """
        functions_data = request.data.get('functions', [])

        if not functions_data:
            return Response(
                {'error': 'Se requiere una lista de funciones'},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_count = 0
        for func_data in functions_data:
            func_id = func_data.get('id')
            order = func_data.get('order')

            if func_id is None or order is None:
                continue

            try:
                function = Function.objects.get(id=func_id)
                function.order = order
                function.save(update_fields=['order'])
                updated_count += 1
            except Function.DoesNotExist:
                pass

        return Response({
            'message': f'{updated_count} funciones reordenadas exitosamente',
            'updated_count': updated_count
        })
