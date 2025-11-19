"""
Category ViewSet for CRUD operations
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.navigation.models import Category
from apps.navigation.serializers import (
    CategorySerializer,
    CategoryListSerializer,
    CategoryCreateUpdateSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Categories
    Categories are used to group functions in the sidebar menu
    """
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination

    def get_queryset(self):
        """Filter queryset based on query params"""
        if getattr(self, 'swagger_fake_view', False):
            return Category.objects.none()

        queryset = Category.objects.all()

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.order_by('order', 'name')

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return CategoryListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        return CategorySerializer

    @swagger_auto_schema(
        tags=['Gestión de categorías'],
        operation_description="Listar todas las categorías del sistema",
        manual_parameters=[
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Filtrar por estado activo (true/false)",
                type=openapi.TYPE_BOOLEAN
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """GET /api/navigation/categories/ - List all categories"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de categorías'],
        operation_description="Obtener detalles de una categoría específica"
    )
    def retrieve(self, request, *args, **kwargs):
        """GET /api/navigation/categories/{id}/ - Get category details"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de categorías'],
        operation_description="Crear una nueva categoría",
        responses={
            201: CategorySerializer,
            400: "Datos inválidos",
            403: "Sin permiso"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        POST /api/navigation/categories/ - Create a new category
        Requires Cerbos permission: category:create
        """
        from apps.permissions.services.cerbos_client import cerbos_service

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='category',
            resource_id='new',
            action='create'
        ):
            return Response({
                'detail': 'No tienes permiso para crear categorías.'
            }, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de categorías'],
        operation_description="Actualizar completamente una categoría",
        responses={
            200: CategorySerializer,
            400: "Datos inválidos",
            403: "Sin permiso",
            404: "Categoría no encontrada"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        PUT /api/navigation/categories/{id}/ - Update category
        Requires Cerbos permission: category:update
        """
        from apps.permissions.services.cerbos_client import cerbos_service

        instance = self.get_object()

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='category',
            resource_id=str(instance.id),
            action='update'
        ):
            return Response({
                'detail': 'No tienes permiso para actualizar esta categoría.'
            }, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de categorías'],
        operation_description="Actualizar parcialmente una categoría",
        responses={
            200: CategorySerializer,
            400: "Datos inválidos",
            403: "Sin permiso",
            404: "Categoría no encontrada"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/navigation/categories/{id}/ - Partial update category"""
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de categorías'],
        operation_description="Eliminar una categoría",
        responses={
            204: "Categoría eliminada exitosamente",
            403: "No se pueden eliminar categorías del sistema",
            404: "Categoría no encontrada"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/navigation/categories/{id}/ - Delete category
        System categories cannot be deleted.
        Requires Cerbos permission: category:delete
        """
        from apps.permissions.services.cerbos_client import cerbos_service

        instance = self.get_object()

        # Prevent deletion of system categories
        if instance.is_system:
            return Response({
                'detail': 'No se pueden eliminar categorías del sistema.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='category',
            resource_id=str(instance.id),
            action='delete'
        ):
            return Response({
                'detail': 'No tienes permiso para eliminar categorías.'
            }, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de categorías'],
        operation_description="Reordenar categorías",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'categories': openapi.Schema(
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
            200: "Categorías reordenadas exitosamente",
            400: "Datos inválidos"
        }
    )
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        POST /api/navigation/categories/reorder/
        Reorder categories by updating their order field
        Expects: { "categories": [{"id": 1, "order": 0}, {"id": 2, "order": 1}, ...] }
        """
        categories_data = request.data.get('categories', [])

        if not categories_data:
            return Response(
                {'error': 'Se requiere una lista de categorías'},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_count = 0
        for cat_data in categories_data:
            cat_id = cat_data.get('id')
            order = cat_data.get('order')

            if cat_id is None or order is None:
                continue

            try:
                category = Category.objects.get(id=cat_id)
                category.order = order
                category.save(update_fields=['order'])
                updated_count += 1
            except Category.DoesNotExist:
                pass

        return Response({
            'message': f'{updated_count} categorías reordenadas exitosamente',
            'updated_count': updated_count
        })

    @swagger_auto_schema(
        tags=['Gestión de categorías'],
        operation_description="Obtener funciones de una categoría",
        responses={200: "Lista de funciones"}
    )
    @action(detail=True, methods=['get'])
    def functions(self, request, pk=None):
        """
        GET /api/navigation/categories/{id}/functions/
        Get all functions belonging to this category
        """
        from apps.navigation.serializers import FunctionListSerializer

        category = self.get_object()
        functions = category.functions.filter(is_active=True).order_by('order', 'name')
        serializer = FunctionListSerializer(functions, many=True)
        return Response(serializer.data)
