"""
RoleAssignment model based on UML diagram
Assigns roles to users with optional scope and expiration
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import TimeStampedModel


class RoleAssignment(TimeStampedModel):
    """
    Role assignment to users.
    Supports scoped roles and expiration dates.

    Fields according to UML diagram:
    - user_id: BigInteger FK - User receiving the role
    - role_id: BigInteger FK - Role being assigned
    - assigned_at: TIMESTAMP - When the role was assigned
    - assigned_by_id: BigInteger FK nullable - User who assigned the role
    - expires_at: TIMESTAMP nullable - When the assignment expires
    - scope_type: VARCHAR(50) nullable - Type of scope (e.g., 'organization', 'project')
    - scope_id: BigInteger nullable - ID of the scoped resource
    - is_active: BOOLEAN - Whether the assignment is currently active
    - created_at: TIMESTAMP
    - updated_at: TIMESTAMP
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='role_assignments',
        verbose_name='Usuario',
        db_index=True
    )

    role = models.ForeignKey(
        'permissions.Role',
        on_delete=models.CASCADE,
        related_name='role_assignments',
        verbose_name='Rol',
        db_index=True
    )

    assigned_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Asignado en'
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='role_assignments_made',
        verbose_name='Asignado por'
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expira en',
        db_index=True,
        help_text='Fecha de expiración de la asignación (opcional)'
    )

    # Scope for scoped roles (e.g., admin of a specific project)
    scope_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Tipo de alcance',
        help_text='Tipo de recurso al que se limita el rol (ej: organization, project)'
    )

    scope_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='ID del alcance',
        help_text='ID del recurso específico al que se limita el rol'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        db_index=True
    )

    class Meta:
        db_table = 'permissions_roleassignment'
        verbose_name = 'Asignación de Rol'
        verbose_name_plural = 'Asignaciones de Roles'
        ordering = ['-assigned_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role', 'scope_type', 'scope_id'],
                name='unique_role_assignment'
            )
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        scope_info = f" ({self.scope_type}:{self.scope_id})" if self.scope_type else ""
        return f"{self.user.email} - {self.role.name}{scope_info}"

    def is_expired(self):
        """Check if the role assignment has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        """Override save to auto-deactivate expired assignments"""
        if self.is_expired() and self.is_active:
            self.is_active = False
        super().save(*args, **kwargs)
