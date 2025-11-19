"""
MenuItem model based on UML diagram
Individual menu items for the sidebar navigation
"""
from django.db import models
from apps.core.models import TimeStampedModel


class MenuItem(TimeStampedModel):
    """
    Menu item for sidebar navigation.
    Supports hierarchical menus and permission-based visibility.

    Fields according to UML diagram:
    - category_id: BigInteger FK - Menu category
    - parent_id: BigInteger FK nullable - Parent menu item (for hierarchical menus)
    - required_role_id: BigInteger FK nullable - Required role to see this item
    - name: VARCHAR(100) - Internal name
    - label: VARCHAR(100) - Display label
    - url: VARCHAR(255) - Route URL
    - description: TEXT nullable - Item description
    - icon: VARCHAR(50) nullable - Icon class or name
    - badge: VARCHAR(50) nullable - Badge text (e.g., "New", "3")
    - badge_variant: VARCHAR(20) nullable - Badge color/variant
    - resource_type: VARCHAR(50) nullable - Resource type for Cerbos check
    - action: VARCHAR(50) nullable - Action for Cerbos check (e.g., 'read', 'create')
    - order: INTEGER - Display order within category
    - is_external: BOOLEAN - Whether the link is external
    - open_in_new_tab: BOOLEAN - Whether to open in new tab
    - is_active: BOOLEAN - Whether the item is active
    - is_system: BOOLEAN - Whether this is a system item (cannot be deleted)
    - created_at: TIMESTAMP
    - updated_at: TIMESTAMP
    """
    category = models.ForeignKey(
        'navigation.MenuCategory',
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='Categoría',
        db_index=True
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Ítem padre',
        db_index=True,
        help_text='Ítem padre para menús jerárquicos'
    )

    required_role = models.ForeignKey(
        'permissions.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menu_items',
        verbose_name='Rol requerido',
        db_index=True,
        help_text='Rol mínimo requerido para ver este ítem'
    )

    name = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre interno del ítem de menú'
    )

    label = models.CharField(
        max_length=100,
        verbose_name='Etiqueta',
        help_text='Etiqueta para mostrar en el menú'
    )

    url = models.CharField(
        max_length=255,
        verbose_name='URL',
        help_text='Ruta o URL del ítem'
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Descripción'
    )

    icon = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Ícono',
        help_text='Clase o nombre del ícono'
    )

    badge = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Insignia',
        help_text='Texto de la insignia (ej: "Nuevo", "3")'
    )

    badge_variant = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Variante de insignia',
        help_text='Color o variante de la insignia (ej: "danger", "success")'
    )

    # Cerbos integration
    resource_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Tipo de recurso',
        help_text='Tipo de recurso para verificación con Cerbos'
    )

    action = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Acción',
        help_text='Acción para verificación con Cerbos (ej: "read", "create")'
    )

    order = models.IntegerField(
        default=0,
        verbose_name='Orden',
        db_index=True,
        help_text='Orden de visualización dentro de la categoría'
    )

    is_external = models.BooleanField(
        default=False,
        verbose_name='Enlace externo'
    )

    open_in_new_tab = models.BooleanField(
        default=False,
        verbose_name='Abrir en nueva pestaña'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        db_index=True
    )

    is_system = models.BooleanField(
        default=False,
        verbose_name='Ítem del sistema',
        help_text='Los ítems del sistema no pueden ser eliminados'
    )

    class Meta:
        db_table = 'navigation_menuitem'
        verbose_name = 'Ítem de Menú'
        verbose_name_plural = 'Ítems de Menú'
        ordering = ['category__order', 'order', 'label']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['parent']),
            models.Index(fields=['required_role']),
            models.Index(fields=['order']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent.label} > {self.label}"
        return f"{self.category.label} - {self.label}"

    def get_children_count(self):
        """Get number of child menu items"""
        return self.children.filter(is_active=True).count()

    def has_children(self):
        """Check if this item has children"""
        return self.children.exists()
