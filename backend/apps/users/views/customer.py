"""
Customer views with Cerbos integration
Customers have read-only access to view their own information
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.users.models import Customer
from apps.users.serializers import (
    CustomerSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer,
    CustomerProfileUpdateSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Gestión de Clientes

    Endpoints para administrar clientes del sistema.
    - Admin/Staff: puede crear, ver, actualizar y eliminar clientes
    - Customers: pueden ver y actualizar solo su propia información (modo consulta)
    """
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Customers']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return CustomerCreateSerializer
        elif self.action in ['update', 'partial_update']:
            # If user is updating themselves, use profile serializer
            if self.action in ['update_me']:
                return CustomerProfileUpdateSerializer
            return CustomerUpdateSerializer
        return CustomerSerializer

    def get_queryset(self):
        """
        Filter queryset based on permissions.
        - Admin/Staff: can see all customers
        - Customers: can only see themselves
        """
        # Skip permission checks during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Customer.objects.none()

        user = self.request.user

        # Admin/Staff can see all customers
        if user.is_superuser or user.is_staff:
            return Customer.objects.all()

        # Customers can only see themselves if they are a customer
        try:
            customer = Customer.objects.get(id=user.id)
            return Customer.objects.filter(id=customer.id)
        except Customer.DoesNotExist:
            return Customer.objects.none()

    @swagger_auto_schema(
        tags=['Gestión de clientes'],
        operation_description="Listar todos los clientes. Admin/Staff puede ver todos, clientes solo se ven a sí mismos.",
        responses={
            200: CustomerSerializer(many=True),
            401: "No autenticado"
        }
    )
    def list(self, request, *args, **kwargs):
        """GET /api/customers/ - List customers"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de clientes'],
        operation_description="Obtener detalles de un cliente específico.",
        responses={
            200: CustomerSerializer(),
            401: "No autenticado",
            403: "Sin permiso",
            404: "Cliente no encontrado"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """GET /api/customers/{id}/ - Get customer details"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de clientes'],
        operation_description="Crear un nuevo cliente. Solo admin/staff.",
        request_body=CustomerCreateSerializer,
        responses={
            201: CustomerSerializer(),
            400: "Datos inválidos",
            401: "No autenticado",
            403: "Solo admin/staff puede crear clientes"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new customer (admin/staff only).
        """
        # Check permission with Cerbos
        from apps.permissions.services.cerbos_client import cerbos_service

        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='customer',
            resource_id='new',
            action='create'
        ):
            return Response({
                'detail': 'No tienes permiso para crear clientes. Solo admin/staff.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()

        return Response(
            CustomerSerializer(customer, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        tags=['Gestión de clientes'],
        operation_description="Actualizar un cliente. Admin/Staff puede actualizar cualquiera, clientes solo a sí mismos (información limitada).",
        request_body=CustomerUpdateSerializer,
        responses={
            200: CustomerSerializer(),
            400: "Datos inválidos",
            401: "No autenticado",
            403: "Sin permiso para actualizar este cliente",
            404: "Cliente no encontrado"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        Update customer.
        Admin/Staff can update any customer.
        Customers can only update their own profile (limited fields).
        """
        from apps.permissions.services.cerbos_client import cerbos_service

        instance = self.get_object()

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='customer',
            resource_id=str(instance.id),
            action='update'
        ):
            return Response({
                'detail': 'No tienes permiso para actualizar este cliente.'
            }, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(CustomerSerializer(instance, context={'request': request}).data)

    @swagger_auto_schema(
        tags=['Gestión de clientes'],
        operation_description="Actualización parcial de un cliente.",
        request_body=CustomerUpdateSerializer,
        responses={
            200: CustomerSerializer(),
            400: "Datos inválidos",
            401: "No autenticado",
            403: "Sin permiso para actualizar este cliente",
            404: "Cliente no encontrado"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/customers/{id}/ - Partial update customer"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Gestión de clientes'],
        operation_description="Eliminar un cliente. Solo admin/staff.",
        responses={
            204: "Cliente eliminado exitosamente",
            401: "No autenticado",
            403: "Solo admin/staff puede eliminar clientes",
            404: "Cliente no encontrado"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete customer (admin/staff only).
        """
        from apps.permissions.services.cerbos_client import cerbos_service

        instance = self.get_object()

        # Check permission with Cerbos
        if not cerbos_service.check_user_permission(
            user=request.user,
            resource_type='customer',
            resource_id=str(instance.id),
            action='delete'
        ):
            return Response({
                'detail': 'No tienes permiso para eliminar clientes. Solo admin/staff.'
            }, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=['Cliente actual'],
        operation_description="Obtener información del cliente actual autenticado.",
        responses={
            200: CustomerSerializer(),
            401: "No autenticado",
            404: "El usuario actual no es un cliente"
        }
    )
    @action(detail=False, methods=['get'], url_path='me')
    def get_me(self, request):
        """
        GET /api/customers/me
        Get current customer information.
        """
        user = request.user

        # Check if current user is a customer
        try:
            customer = Customer.objects.get(id=user.id)
            serializer = CustomerSerializer(customer, context={'request': request})
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({
                'detail': 'El usuario actual no es un cliente.'
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        methods=['patch', 'put'],
        tags=['Cliente actual'],
        operation_description="Actualizar perfil del cliente actual. Permite editar datos personales limitados.",
        request_body=CustomerProfileUpdateSerializer,
        responses={
            200: CustomerSerializer,
            400: "Datos inválidos",
            401: "No autenticado",
            404: "El usuario actual no es un cliente"
        }
    )
    @action(detail=False, methods=['patch', 'put'], url_path='me/update')
    def update_me(self, request):
        """
        PATCH/PUT /api/customers/me/update
        Update current customer profile.
        Customers can only update their own limited personal information.
        """
        user = request.user

        # Check if current user is a customer
        try:
            customer = Customer.objects.get(id=user.id)
        except Customer.DoesNotExist:
            return Response({
                'detail': 'El usuario actual no es un cliente.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerProfileUpdateSerializer(
            customer,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return complete customer data
        return Response(CustomerSerializer(customer, context={'request': request}).data)

    @swagger_auto_schema(
        tags=['Cliente actual'],
        operation_description="Obtener permisos del cliente actual.",
        responses={
            200: openapi.Response(
                description="Permisos del cliente",
                examples={
                    "application/json": {
                        "customer_id": 1,
                        "email": "cliente@example.com",
                        "permissions": {
                            "customers": {
                                "read": True,
                                "update": False
                            }
                        }
                    }
                }
            ),
            401: "No autenticado",
            404: "El usuario actual no es un cliente"
        }
    )
    @action(detail=False, methods=['get'], url_path='me/permissions')
    def get_my_permissions(self, request):
        """
        GET /api/customers/me/permissions
        Get current customer permissions.
        Customers typically have read-only access.
        """
        from apps.permissions.services.cerbos_client import cerbos_service

        user = request.user

        # Check if current user is a customer
        try:
            customer = Customer.objects.get(id=user.id)
        except Customer.DoesNotExist:
            return Response({
                'detail': 'El usuario actual no es un cliente.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get permissions for 'customer' resource
        customer_perms = cerbos_service.get_user_permissions_for_resource(
            user=user,
            resource_type='customer',
            resource_id=str(customer.id)
        )

        return Response({
            'customer_id': customer.id,
            'email': customer.email,
            'customer_code': customer.customer_code,
            'permissions': {
                'customers': {
                    'read': customer_perms.get('read', False),
                    'update': customer_perms.get('update', False),
                    'delete': customer_perms.get('delete', False),
                }
            }
        })
