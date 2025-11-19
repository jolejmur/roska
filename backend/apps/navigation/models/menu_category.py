"""
MenuCategory model based on UML diagram
Categories for organizing menu items in the sidebar
"""
from django.db import models
from apps.core.models import TimeStampedModel


class MenuCategory(TimeStampedModel):
    """
    Menu category for organizing sidebar items.

    Fields according to UML diagram:
    - name: VARCHAR(100) unique - Internal name
    - label: VARCHAR(100) - Display label
    - description: TEXT nullable - Category description
    - icon: VARCHAR(50) - Icon class or name
    - color: VARCHAR(20) - Color for the category
    - order: INTEGER - Display order
    - is_active: BOOLEAN - Whether the category is active
    - is_system: BOOLEAN - Whether this is a system category (cannot be deleted)
    - created_at: TIMESTAMP
    - updated_at: TIMESTAMP
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre',
        help_text='Nombre interno de la categoría'
    )

    label = models.CharField(
        max_length=100,
        verbose_name='Etiqueta',
        help_text='Etiqueta para mostrar en el sidebar'
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Descripción'
    )

    icon = models.CharField(
        max_length=50,
        verbose_name='Ícono',
        help_text='Clase o nombre del ícono (ej: fa-dashboard, material-icons)'
    )

    color = models.CharField(
        max_length=20,
        verbose_name='Color',
        help_text='Color hex o nombre de clase para la categoría'
    )

    order = models.IntegerField(
        default=0,
        verbose_name='Orden',
        db_index=True,
        help_text='Orden de visualización (menor número aparece primero)'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa',
        db_index=True
    )

    is_system = models.BooleanField(
        default=False,
        verbose_name='Categoría del sistema',
        help_text='Las categorías del sistema no pueden ser eliminadas'
    )

    class Meta:
        db_table = 'navigation_menucategory'
        verbose_name = 'Categoría de Menú'
        verbose_name_plural = 'Categorías de Menú'
        ordering = ['order', 'label']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.label

    def get_active_items_count(self):
        """Get number of active menu items in this category"""
        return self.menuitem_set.filter(is_active=True).count()
