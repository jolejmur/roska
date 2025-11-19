"""
Category model for organizing functions in the sidebar menu
"""
from django.db import models
from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    Category model for grouping functions in the sidebar.
    Categories act as folders/sections in the menu.

    Example categories:
    - Gestión de Usuarios (users_management)
    - Configuración del Sistema (system_config)
    - Reportes (reports)
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre descriptivo de la categoría (ej: "Gestión de Usuarios")'
    )

    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Código',
        help_text='Código único para identificar la categoría (ej: "users_management")'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción',
        help_text='Descripción de la categoría'
    )

    icon = models.CharField(
        max_length=100,
        verbose_name='Icono',
        help_text='Clase CSS del icono (ej: "fas fa-users")',
        default='fas fa-folder'
    )

    color = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Color',
        help_text='Color hex o nombre para la categoría (ej: "#3498db", "primary")'
    )

    order = models.IntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden de aparición en el menú (menor = primero)'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa',
        help_text='Si la categoría está activa o no'
    )

    is_system = models.BooleanField(
        default=False,
        verbose_name='Categoría del sistema',
        help_text='Las categorías del sistema no pueden ser eliminadas'
    )

    class Meta:
        db_table = 'navigation_categories'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['order']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_active_functions_count(self):
        """Retorna el número de funciones activas en esta categoría"""
        return self.functions.filter(is_active=True).count()
