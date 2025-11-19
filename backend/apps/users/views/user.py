"""
User views with Cerbos integration
Migrated from FastAPI users endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.users.models import User
from apps.users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ProfileUpdateSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    Gestión de Usuarios

    Endpoints para administrar usuarios del sistema con integración de permisos Cerbos.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Users']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Filter queryset based on permissions.
        Regular users can only see themselves.
        Superusers can see all users.
        """
        # Skip permission checks during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()

        user = self.request.user

        # SIMPLIFIED: Superusers see all, regular users see only themselves
        if user.is_superuser or user.is_staff:
            return User.objects.all()

        # Otherwise, only return the current user
        return User.objects.filter(id=user.id)

    @swagger_auto_schema(
        tags=['Gestión de usuarios'],
        operation_description="Listar todos los usuarios. Superadmin puede ver todos, usuarios regulares solo se ven a sí mismos.",
        responses={
            200: UserSerializer(many=True),
            401: "No autenticado"
        }
    )
    def list(self, request, *args, **kwargs):
        """GET /api/users/ - List users"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de usuarios'],
        operation_description="Obtener detalles de un usuario específico.",
        responses={
            200: UserSerializer(),
            401: "No autenticado",
            403: "Sin permiso",
            404: "Usuario no encontrado"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """GET /api/users/{id}/ - Get user details"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de usuarios'],
        operation_description="Crear un nuevo usuario. Solo superadmin.",
        request_body=UserCreateSerializer,
        responses={
            201: UserSerializer(),
            400: "Datos inválidos",
            401: "No autenticado",
            403: "Solo superadmin puede crear usuarios"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new user (superadmin only).
        Migrated from FastAPI POST /users endpoint.
        """
        # Import here to avoid circular imports
        from apps.permissions.services.cerbos_client import cerbos_service

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='user',
            resource_id='new',
            action='create'
        ):
            return Response({
                'detail': 'No tienes permiso para crear usuarios. Solo superadmin.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        tags=['Gestión de usuarios'],
        operation_description="Actualizar un usuario. Usuarios pueden actualizarse a sí mismos, superadmin puede actualizar cualquiera.",
        request_body=UserUpdateSerializer,
        responses={
            200: UserSerializer(),
            400: "Datos inválidos",
            401: "No autenticado",
            403: "Sin permiso para actualizar este usuario",
            404: "Usuario no encontrado"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        Update user.
        Users can only update themselves unless they are superadmin.
        """
        # Import here to avoid circular imports
        from apps.permissions.services.cerbos_client import cerbos_service

        instance = self.get_object()

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='user',
            resource_id=str(instance.id),
            action='update'
        ):
            return Response({
                'detail': 'No tienes permiso para actualizar este usuario.'
            }, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(UserSerializer(instance).data)

    @swagger_auto_schema(
        tags=['Gestión de usuarios'],
        operation_description="Actualización parcial de un usuario. Usuarios pueden actualizarse a sí mismos, superadmin puede actualizar cualquiera.",
        request_body=UserUpdateSerializer,
        responses={
            200: UserSerializer(),
            400: "Datos inválidos",
            401: "No autenticado",
            403: "Sin permiso para actualizar este usuario",
            404: "Usuario no encontrado"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/users/{id}/ - Partial update user"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de usuarios'],
        operation_description="Eliminar un usuario. Solo superadmin.",
        responses={
            204: "Usuario eliminado exitosamente",
            401: "No autenticado",
            403: "Solo superadmin puede eliminar usuarios",
            404: "Usuario no encontrado"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete user (superadmin only).
        """
        # Import here to avoid circular imports
        from apps.permissions.services.cerbos_client import cerbos_service

        instance = self.get_object()

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='user',
            resource_id=str(instance.id),
            action='delete'
        ):
            return Response({
                'detail': 'No tienes permiso para eliminar usuarios. Solo superadmin.'
            }, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=['Usuario actual'],
        operation_description="Obtener información del usuario actual autenticado.",
        responses={
            200: UserSerializer(),
            401: "No autenticado"
        }
    )
    @action(detail=False, methods=['get'], url_path='me')
    def get_me(self, request):
        """
        GET /api/users/me
        Get current user information.
        Compatible with FastAPI /users/me endpoint.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Usuario actual'],
        operation_description="Obtener permisos del usuario actual organizados por recurso.",
        responses={
            200: openapi.Response(
                description="Permisos del usuario",
                examples={
                    "application/json": {
                        "user_id": 1,
                        "email": "admin@example.com",
                        "is_superuser": True,
                        "permissions": {
                            "users": {
                                "create": True,
                                "read": True,
                                "update": True,
                                "delete": True,
                                "list": True
                            }
                        }
                    }
                }
            ),
            401: "No autenticado"
        }
    )
    @action(detail=False, methods=['get'], url_path='me/permissions')
    def get_my_permissions(self, request):
        """
        GET /api/users/me/permissions
        Get current user permissions organized by resource.
        Migrated from FastAPI endpoint.
        """
        # Import here to avoid circular imports
        from apps.permissions.services.cerbos_client import cerbos_service

        user = request.user

        # Get permissions for 'user' resource
        user_perms = cerbos_service.get_user_permissions_for_resource(
            user=user,
            resource_type='user',
            resource_id='generic'
        )

        return Response({
            'user_id': user.id,
            'email': user.email,
            'is_superuser': user.is_superuser,
            'permissions': {
                'users': {
                    'create': user_perms.get('create', False),
                    'read': user_perms.get('read', False),
                    'update': user_perms.get('update', False),
                    'delete': user_perms.get('delete', False),
                    'list': user_perms.get('list', False),
                }
            }
        })

    @swagger_auto_schema(
        tags=['Usuario actual'],
        operation_description="Obtener menú dinámico del usuario actual basado en sus roles y funciones asignadas.",
        responses={
            200: openapi.Response(
                description="Menú dinámico del usuario",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "name": "Mi Perfil",
                            "code": "profile",
                            "url": "/profile",
                            "icon": "fas fa-user",
                            "order": 0,
                            "children": []
                        },
                        {
                            "id": 2,
                            "name": "Gestión de Usuarios",
                            "code": "users",
                            "url": None,
                            "icon": "fas fa-users",
                            "order": 10,
                            "children": [
                                {
                                    "id": 3,
                                    "name": "Usuarios",
                                    "code": "users.list",
                                    "url": "/users",
                                    "icon": "fas fa-user-friends",
                                    "order": 0,
                                    "children": []
                                }
                            ]
                        }
                    ]
                }
            ),
            401: "No autenticado"
        }
    )
    @action(detail=False, methods=['get'], url_path='me/menu')
    def get_my_menu(self, request):
        """
        GET /api/users/me/menu
        Get dynamic menu for current user based on their roles and assigned functions.
        Functions are grouped by categories (collapsible sections).
        """
        user = request.user

        # Import models here to avoid circular imports
        from apps.permissions.models import RoleAssignment
        from apps.navigation.models import Function, Category

        # Get all active role assignments for the user
        role_assignments = RoleAssignment.objects.filter(
            user=user,
            is_active=True,
            role__is_active=True
        ).select_related('role').prefetch_related('role__functions')

        # Collect all unique functions from all roles
        functions_dict = {}

        for assignment in role_assignments:
            role = assignment.role
            for function in role.functions.filter(is_active=True):
                if function.id not in functions_dict:
                    functions_dict[function.id] = function

        all_functions = list(functions_dict.values())

        # Get all unique categories from the functions
        category_ids = {f.category_id for f in all_functions if f.category_id}
        categories = Category.objects.filter(id__in=category_ids, is_active=True).order_by('order', 'name')

        # Build menu structure grouped by categories
        menu = []

        # 1. Add functions WITHOUT category first (root level items like "Mi Perfil")
        root_functions = [f for f in all_functions if not f.category_id]
        root_functions.sort(key=lambda f: (f.order, f.name))

        for func in root_functions:
            menu.append({
                'id': func.id,
                'name': func.name,
                'code': func.code,
                'url': func.url,
                'icon': func.icon,
                'order': func.order,
            })

        # 2. Add categories with their functions as children
        for category in categories:
            # Get functions belonging to this category
            category_functions = [f for f in all_functions if f.category_id == category.id]
            category_functions.sort(key=lambda f: (f.order, f.name))

            if category_functions:  # Only add category if it has functions
                category_item = {
                    'id': f'cat_{category.id}',
                    'name': category.name,
                    'code': category.code,
                    'icon': category.icon,
                    'color': category.color,
                    'order': category.order,
                    'is_category': True,
                    'children': [
                        {
                            'id': f.id,
                            'name': f.name,
                            'code': f.code,
                            'url': f.url,
                            'icon': f.icon,
                            'order': f.order,
                        }
                        for f in category_functions
                    ]
                }
                menu.append(category_item)

        # Sort final menu by order
        menu.sort(key=lambda x: x['order'])

        return Response(menu)

    @swagger_auto_schema(
        methods=['patch', 'put'],
        tags=['Usuario actual'],
        operation_description="Actualizar perfil del usuario actual. Permite editar datos personales como CI, teléfono, foto, dirección, etc. NO permite editar permisos o roles.",
        request_body=ProfileUpdateSerializer,
        responses={
            200: UserSerializer,
            400: "Datos inválidos",
            401: "No autenticado"
        }
    )
    @action(detail=False, methods=['patch', 'put'], url_path='me/update')
    def update_me(self, request):
        """
        PATCH/PUT /api/users/me/update
        Update current user profile.
        Users can only update their own personal information.
        """
        user = request.user
        serializer = ProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return complete user data
        return Response(UserSerializer(user, context={'request': request}).data)
