"""
Role model based on UML diagram
Django guarda los roles, Cerbos evalúa permisos CRUD
"""
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class Role(TimeStampedModel):
    """
    Role model for permission management.
    Roles are stored in Django, but CRUD permissions are evaluated by Cerbos.

    Fields according to UML diagram:
    - name: VARCHAR(100) unique - Display name
    - code: VARCHAR(50) unique - Internal code for the role
    - description: TEXT - Role description
    - cerbos_role: VARCHAR(100) - Corresponding role in Cerbos
    - is_active: BOOLEAN - Whether the role is active
    - is_system: BOOLEAN - Whether this is a system role (cannot be deleted)
    - level: INTEGER - Role hierarchy level (higher = more permissions)
    - created_by_id: BigInteger FK nullable - User who created this role
    - created_at: TIMESTAMP
    - updated_at: TIMESTAMP
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre',
        help_text='Nombre para mostrar del rol'
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        db_index=True,
        help_text='Código interno del rol (ej: ADMIN, MANAGER, USER)'
    )

    description = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción detallada del rol y sus permisos'
    )

    cerbos_role = models.CharField(
        max_length=100,
        verbose_name='Rol en Cerbos',
        db_index=True,
        help_text='Nombre del rol correspondiente en las políticas de Cerbos'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        db_index=True
    )

    is_system = models.BooleanField(
        default=False,
        verbose_name='Rol del sistema',
        help_text='Los roles del sistema no pueden ser eliminados'
    )

    level = models.IntegerField(
        default=0,
        verbose_name='Nivel jerárquico',
        help_text='Nivel de jerarquía del rol (mayor número = más permisos)'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles_created',
        verbose_name='Creado por'
    )

    functions = models.ManyToManyField(
        'navigation.Function',
        blank=True,
        related_name='roles',
        verbose_name='Funciones',
        help_text='Funciones del menú asignadas a este rol'
    )

    class Meta:
        db_table = 'permissions_role'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['-level', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['cerbos_role']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def get_users_count(self):
        """Get number of users assigned to this role"""
        return self.roleassignment_set.filter(is_active=True).count()
